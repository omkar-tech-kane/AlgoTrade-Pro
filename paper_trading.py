import os
import json
import pandas as pd

from risk_management import (
    INITIAL_CAPITAL,
    calculate_position_size,
    check_exit
)

TRANSACTION_FEE = 0.001

PORTFOLIO_FOLDER = "reports/paper_portfolios"


# =====================================
# CREATE PORTFOLIO STORAGE
# =====================================

def create_storage():

    os.makedirs(
        PORTFOLIO_FOLDER,
        exist_ok=True
    )


# =====================================
# GET PORTFOLIO FILE
# =====================================

def get_portfolio_file(symbol):

    safe_symbol = symbol.replace(".", "_").replace("/", "_")

    return os.path.join(
        PORTFOLIO_FOLDER,
        f"{safe_symbol}.json"
    )


# =====================================
# INITIALIZE PORTFOLIO
# =====================================

def create_new_portfolio():

    return {
        "cash": float(INITIAL_CAPITAL),
        "shares": 0,
        "entry_price": 0.0,
        "position_cost": 0.0,
        "trades": [],
        "equity_history": {},
        "last_processed_timestamp": None
    }


# =====================================
# LOAD PORTFOLIO
# =====================================

def load_portfolio(symbol):

    create_storage()

    file_path = get_portfolio_file(symbol)

    if not os.path.exists(file_path):

        return create_new_portfolio()

    with open(file_path, "r") as file:

        return json.load(file)


# =====================================
# SAVE PORTFOLIO
# =====================================

def save_portfolio(symbol, portfolio):

    create_storage()

    file_path = get_portfolio_file(symbol)

    temp_path = file_path + ".tmp"

    with open(temp_path, "w") as file:

        json.dump(
            portfolio,
            file,
            indent=4
        )

    os.replace(temp_path, file_path)


# =====================================
# SIMULATE PAPER TRADING
# =====================================

def simulate_trading(data, symbol="DEFAULT", persistent=False):

    if data.empty:
        raise ValueError("No market data available.")

    required_columns = ["Close", "Signal"]

    for column in required_columns:

        if column not in data.columns:
            raise ValueError(f"Missing column: {column}")

    data = data.copy()

    # =================================
    # LOAD OR CREATE PORTFOLIO
    # =================================

    if persistent:

        portfolio = load_portfolio(symbol)

    else:

        portfolio = create_new_portfolio()

    cash = float(portfolio["cash"])
    shares = int(portfolio["shares"])

    entry_price = float(portfolio["entry_price"])
    position_cost = float(portfolio["position_cost"])

    trades = portfolio["trades"]
    equity_history = portfolio["equity_history"]

    last_processed = portfolio["last_processed_timestamp"]

    # =================================
    # FIRST-TIME INITIALIZATION
    # =================================

    if persistent and last_processed is None:

        if len(data) < 2:
            raise ValueError(
                "At least two candles are required."
            )

        # Start the virtual portfolio at the latest candle.
        # Earlier historical candles are not traded.
        last_processed = data.index[-2].isoformat()

    # =================================
    # IDENTIFY NEW CANDLES
    # =================================

    if last_processed is None:

        new_data = data

    else:

        last_timestamp = pd.Timestamp(last_processed)

        new_data = data[
            data.index > last_timestamp
        ]

    # =================================
    # PROCESS NEW CANDLES
    # =================================

    for timestamp, row in new_data.iterrows():

        price = float(row["Close"])

        if pd.isna(price) or price <= 0:
            continue

        # Get the previous candle's signal
        position = data.index.get_loc(timestamp)

        if position > 0:

            previous_signal = data["Signal"].iloc[position - 1]

            signal = (
                0 if pd.isna(previous_signal)
                else int(previous_signal)
            )

        else:

            signal = 0

        action = "HOLD"

        # -----------------------------
        # EXIT POSITION
        # -----------------------------

        if shares > 0:

            exit_reason = check_exit(
                entry_price,
                price
            )

            if exit_reason == "HOLD" and signal == -1:

                exit_reason = "SELL_SIGNAL"

            if exit_reason != "HOLD":

                revenue = shares * price

                fee = revenue * TRANSACTION_FEE

                net_revenue = revenue - fee

                realized_pnl = net_revenue - position_cost

                cash += net_revenue

                trades.append({
                    "Date": timestamp.isoformat(),
                    "Action": "SELL",
                    "Reason": exit_reason,
                    "Price": price,
                    "Quantity": shares,
                    "Fee": fee,
                    "Realized_PnL": realized_pnl
                })

                shares = 0
                entry_price = 0.0
                position_cost = 0.0

                action = "SELL"

        # -----------------------------
        # ENTER POSITION
        # -----------------------------

        if signal == 1 and shares == 0 and action != "SELL":

            sizing = calculate_position_size(
                cash,
                price
            )

            quantity = sizing["Quantity"]

            cost = quantity * price

            fee = cost * TRANSACTION_FEE

            total_cost = cost + fee

            if quantity > 0 and total_cost <= cash:

                cash -= total_cost

                shares = quantity

                entry_price = price

                position_cost = total_cost

                trades.append({
                    "Date": timestamp.isoformat(),
                    "Action": "BUY",
                    "Reason": "BUY_SIGNAL",
                    "Price": price,
                    "Quantity": quantity,
                    "Fee": fee,
                    "Realized_PnL": 0.0
                })

                action = "BUY"

        # -----------------------------
        # UPDATE EQUITY
        # -----------------------------

        portfolio_value = cash + shares * price

        equity_history[timestamp.isoformat()] = portfolio_value

        last_processed = timestamp.isoformat()

    # =================================
    # UPDATE PORTFOLIO STATE
    # =================================

    portfolio["cash"] = cash
    portfolio["shares"] = shares
    portfolio["entry_price"] = entry_price
    portfolio["position_cost"] = position_cost
    portfolio["trades"] = trades
    portfolio["equity_history"] = equity_history
    portfolio["last_processed_timestamp"] = last_processed

    if persistent:

        save_portfolio(symbol, portfolio)

    # =================================
    # ADD RESULTS TO DATAFRAME
    # =================================

    data["Equity"] = [
        equity_history.get(timestamp.isoformat(), float("nan"))
        for timestamp in data.index
    ]

    data["Executed_Action"] = "HOLD"

    # Mark newly executed trades
    for trade in trades:

        trade_time = pd.Timestamp(trade["Date"])

        if trade_time in data.index:

            data.loc[
                trade_time,
                "Executed_Action"
            ] = trade["Action"]

    # =================================
    # FINAL PORTFOLIO VALUE
    # =================================

    latest_price = float(data["Close"].iloc[-1])

    final_value = cash + shares * latest_price

    profit_loss = final_value - INITIAL_CAPITAL

    total_return = (
        profit_loss / INITIAL_CAPITAL
    ) * 100

    # =================================
    # DISPLAY RESULTS
    # =================================

    print("\n========== PERSISTENT PAPER TRADING ==========")

    print(f"Stock: {symbol}")

    print(f"Initial Capital: Rs. {INITIAL_CAPITAL:,.2f}")

    print(f"Available Cash: Rs. {cash:,.2f}")

    print(f"Remaining Shares: {shares}")

    print(f"Latest Price: Rs. {latest_price:,.2f}")

    print(f"Portfolio Value: Rs. {final_value:,.2f}")

    print(f"Profit/Loss: Rs. {profit_loss:,.2f}")

    print(f"Total Return: {total_return:.2f}%")

    print(f"Total Transactions: {len(trades)}")

    # =================================
    # RETURN RESULTS
    # =================================

    return data, trades