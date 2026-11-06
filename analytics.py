import pandas as pd


def calculate_performance(data, trades, initial_capital=100000):

    print("\n========== PERFORMANCE ANALYTICS ==========")

    # Extract completed SELL transactions
    closed_trades = [
        trade for trade in trades
        if trade["Action"] == "SELL"
    ]

    if not closed_trades:
        print("No completed trades available.")
        return None

    # Extract realized profits and losses
    pnl = pd.Series(
        [trade["Realized_PnL"] for trade in closed_trades],
        dtype=float
    )

    winning = pnl[pnl > 0]
    losing = pnl[pnl < 0]

    total_trades = len(pnl)
    winning_trades = len(winning)
    losing_trades = len(losing)

    win_rate = (winning_trades / total_trades) * 100

    gross_profit = winning.sum()
    gross_loss = abs(losing.sum())
    net_profit = pnl.sum()
    average_pnl = pnl.mean()

    if gross_loss > 0:
        profit_factor = gross_profit / gross_loss
    elif gross_profit > 0:
        profit_factor = float("inf")
    else:
        profit_factor = 0

    # Calculate maximum drawdown
    equity = data["Equity"]
    peak = equity.cummax()
    drawdown = (equity - peak) / peak
    max_drawdown = abs(drawdown.min()) * 100

    # Display report
    print(f"Total Closed Trades: {total_trades}")
    print(f"Winning Trades: {winning_trades}")
    print(f"Losing Trades: {losing_trades}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Gross Profit: Rs. {gross_profit:.2f}")
    print(f"Gross Loss: Rs. {gross_loss:.2f}")
    print(f"Net Realized P/L: Rs. {net_profit:.2f}")
    print(f"Average P/L: Rs. {average_pnl:.2f}")
    print(f"Profit Factor: {profit_factor:.2f}")
    print(f"Maximum Drawdown: {max_drawdown:.2f}%")

    # Save report
    report = pd.DataFrame({
        "Metric": [
            "Total Closed Trades",
            "Winning Trades",
            "Losing Trades",
            "Win Rate",
            "Gross Profit",
            "Gross Loss",
            "Net Realized P/L",
            "Average P/L",
            "Profit Factor",
            "Maximum Drawdown"
        ],
        "Value": [
            total_trades,
            winning_trades,
            losing_trades,
            win_rate,
            gross_profit,
            gross_loss,
            net_profit,
            average_pnl,
            profit_factor,
            max_drawdown
        ]
    })

    report.to_csv(
        "reports/performance_report.csv",
        index=False
    )

    print("\nPerformance report saved successfully!")

    return report


def calculate_backtest_summary(data, initial_capital=100000):

    if data.empty:
        raise ValueError("Backtest data is empty.")

    final_value = float(data["Equity"].iloc[-1])

    strategy_return = (
        (final_value - initial_capital) / initial_capital
    ) * 100

    first_price = float(data["Close"].iloc[0])
    last_price = float(data["Close"].iloc[-1])

    buy_hold_return = (
        (last_price - first_price) / first_price
    ) * 100

    equity = data["Equity"]

    # Include initial capital in drawdown calculation
    equity_with_initial = pd.concat([
        pd.Series([initial_capital]),
        equity.reset_index(drop=True)
    ])

    peak = equity_with_initial.cummax()
    drawdown = (equity_with_initial - peak) / peak

    max_drawdown = abs(drawdown.min()) * 100

    print("\n========== BACKTEST SUMMARY ==========")
    print(f"Strategy Return: {strategy_return:.2f}%")
    print(f"Buy & Hold Return: {buy_hold_return:.2f}%")
    print(f"Maximum Drawdown: {max_drawdown:.2f}%")

    return {
        "Strategy Return": strategy_return,
        "Buy & Hold Return": buy_hold_return,
        "Maximum Drawdown": max_drawdown
    }


def split_data(data, train_ratio=0.70):
    """
    Split historical data into training and testing periods.
    First 70%: Training data
    Last 30%: Testing data
    """

    if not 0 < train_ratio < 1:
        raise ValueError("train_ratio must be between 0 and 1.")

    if len(data) < 100:
        raise ValueError("At least 100 records are required.")

    split_index = int(len(data) * train_ratio)

    train_data = data.iloc[:split_index].copy()
    test_data = data.iloc[split_index:].copy()

    print("\n========== OUT-OF-SAMPLE DATA SPLIT ==========")
    print(f"Total records: {len(data)}")
    print(f"Training records: {len(train_data)}")
    print(f"Testing records: {len(test_data)}")

    return train_data, test_data