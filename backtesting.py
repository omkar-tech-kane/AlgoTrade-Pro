import pandas as pd

INITIAL_CAPITAL = 100000
MAX_ALLOCATION = 0.20
STOP_LOSS_PERCENT = 0.02
TAKE_PROFIT_PERCENT = 0.04
TRANSACTION_FEE = 0.001


def run_backtest(data):

    if data.empty:
        raise ValueError("No historical data available.")

    required = ["Close", "Signal"]

    for column in required:
        if column not in data.columns:
            raise ValueError(f"Missing column: {column}")

    data = data.copy()

    cash = float(INITIAL_CAPITAL)
    shares = 0
    entry_price = 0.0
    position_cost = 0.0

    trades = []
    equity_values = []

    # Use the previous candle's signal.
    for i in range(1, len(data)):

        price = float(data["Close"].iloc[i])

        if pd.isna(price) or price <= 0:
            continue

        previous_signal = data["Signal"].iloc[i - 1]

        signal = (
            int(previous_signal)
            if pd.notna(previous_signal)
            else 0
        )

        timestamp = data.index[i]
        action = "HOLD"

        # EXIT POSITION
        if shares > 0:

            stop_loss = entry_price * (
                1 - STOP_LOSS_PERCENT
            )

            take_profit = entry_price * (
                1 + TAKE_PROFIT_PERCENT
            )

            exit_reason = None

            if price <= stop_loss:
                exit_reason = "STOP_LOSS"

            elif price >= take_profit:
                exit_reason = "TAKE_PROFIT"

            elif signal == -1:
                exit_reason = "SELL_SIGNAL"

            if exit_reason:

                revenue = shares * price
                fee = revenue * TRANSACTION_FEE
                net_revenue = revenue - fee

                realized_pnl = (
                    net_revenue - position_cost
                )

                cash += net_revenue

                trades.append({
                    "Date": timestamp,
                    "Action": "SELL",
                    "Reason": exit_reason,
                    "Price": price,
                    "Quantity": shares,
                    "Realized_PnL": realized_pnl
                })

                shares = 0
                entry_price = 0.0
                position_cost = 0.0

                action = "SELL"

        # ENTER POSITION
        if signal == 1 and shares == 0 and action != "SELL":

            allocation = cash * MAX_ALLOCATION

            quantity = int(
                allocation / (price * (1 + TRANSACTION_FEE))
            )

            cost = quantity * price
            fee = cost * TRANSACTION_FEE
            total_cost = cost + fee

            if quantity > 0 and total_cost <= cash:

                cash -= total_cost

                shares = quantity
                entry_price = price
                position_cost = total_cost

                trades.append({
                    "Date": timestamp,
                    "Action": "BUY",
                    "Reason": "BUY_SIGNAL",
                    "Price": price,
                    "Quantity": quantity,
                    "Realized_PnL": 0.0
                })

                action = "BUY"

        portfolio_value = cash + shares * price

        equity_values.append({
            "Date": timestamp,
            "Portfolio_Value": portfolio_value,
            "Action": action
        })

    # CLOSE ANY REMAINING POSITION AT FINAL CLOSE
    if shares > 0:

        final_price = float(data["Close"].iloc[-1])

        revenue = shares * final_price
        fee = revenue * TRANSACTION_FEE
        net_revenue = revenue - fee

        realized_pnl = net_revenue - position_cost

        cash += net_revenue

        trades.append({
            "Date": data.index[-1],
            "Action": "SELL",
            "Reason": "BACKTEST_END",
            "Price": final_price,
            "Quantity": shares,
            "Realized_PnL": realized_pnl
        })

        shares = 0

    final_value = cash

    total_return = (
        (final_value - INITIAL_CAPITAL)
        / INITIAL_CAPITAL
    ) * 100

    # PERFORMANCE METRICS
    closed_trades = [
        trade for trade in trades
        if trade["Action"] == "SELL"
    ]

    winning_trades = [
        trade for trade in closed_trades
        if trade["Realized_PnL"] > 0
    ]

    losing_trades = [
        trade for trade in closed_trades
        if trade["Realized_PnL"] < 0
    ]

    win_rate = (
        len(winning_trades) / len(closed_trades) * 100
        if closed_trades else 0
    )

    equity_df = pd.DataFrame(equity_values)

    if not equity_df.empty:

        peak = equity_df["Portfolio_Value"].cummax()

        drawdown = (
            (equity_df["Portfolio_Value"] - peak) / peak
        ) * 100

        max_drawdown = abs(float(drawdown.min()))

    else:
        max_drawdown = 0.0

    metrics = {
        "Initial Capital": INITIAL_CAPITAL,
        "Final Capital": final_value,
        "Total Return (%)": total_return,
        "Total Trades": len(closed_trades),
        "Winning Trades": len(winning_trades),
        "Losing Trades": len(losing_trades),
        "Win Rate (%)": win_rate,
        "Maximum Drawdown (%)": max_drawdown
    }

    return equity_df, trades, metrics