from data_check import get_stock_data
from strategy import generate_signals
from analytics import split_data, calculate_backtest_summary
from paper_trading import simulate_trading

# 1. Download historical data
data = get_stock_data("RELIANCE.NS")

# 2. Split training and testing data
train_data, test_data = split_data(data)

# 3. Generate strategy indicators
signal_data = generate_signals(data)

# 4. Keep the last training row as signal context
split_index = len(train_data)
oos_input = signal_data.iloc[split_index - 1:].copy()

# 5. Run paper trading on the test period
results, trades = simulate_trading(oos_input)

# 6. Remove the training context row
oos_results = results.iloc[1:].copy()

if oos_results.empty:
    raise ValueError("Testing period is empty.")

# 7. Calculate testing performance
print("\n========== OUT-OF-SAMPLE BACKTEST ==========")

summary = calculate_backtest_summary(oos_results)

print("\nTesting Start:", oos_results.index[0])
print("Testing End:", oos_results.index[-1])

closed_trades = [
    trade for trade in trades
    if trade["Action"] == "SELL"
]

print("Completed Trades:", len(closed_trades))

print("\nOUT-OF-SAMPLE BACKTEST COMPLETED!")