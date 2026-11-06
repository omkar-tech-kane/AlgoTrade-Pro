from data_check import get_stock_data
from strategy import generate_signals

# Download stock data
data = get_stock_data("RELIANCE.NS")

# Generate trading signals
data = generate_signals(data)

# Display results
print("\nLATEST STRATEGY ANALYSIS")

print(
    data[
        ["Close", "SMA20", "SMA50", "Signal"]
    ].tail(15)
)

# Count signals
buy_count = (data["Signal"] == 1).sum()

sell_count = (data["Signal"] == -1).sum()

print("\nSTRATEGY REPORT")

print("BUY Signals:", buy_count)

print("SELL Signals:", sell_count)

print("\nStrategy working successfully!")