from data_check import get_stock_data

from strategy import generate_signals

from paper_trading import simulate_trading

from analytics import calculate_performance, calculate_backtest_summary


# Download historical data
data = get_stock_data("RELIANCE.NS")

# Generate trading signals
data = generate_signals(data)

# Run paper trading
results, trades = simulate_trading(data)

# Calculate performance
calculate_performance(results, trades)
calculate_backtest_summary(results)

print("\nANALYTICS TEST COMPLETED!")