from data_check import get_stock_data

from strategy import generate_signals

from paper_trading import simulate_trading


# Step 1: Download stock data

data = get_stock_data("RELIANCE.NS")


# Step 2: Generate signals

data = generate_signals(data)


# Step 3: Run paper trading

results, trades = simulate_trading(data)


# Step 4: Display trade history

print("\n========== TRADE HISTORY ==========")

for trade in trades:

    print(trade)


# Step 5: Save reports

results.to_csv(
    "reports/paper_trading_results.csv"
)

import pandas as pd

trade_df = pd.DataFrame(trades)

trade_df.to_csv(
    "reports/trade_history.csv",
    index=False
)

print("\nReports saved successfully!")

print("\nPAPER TRADING TEST COMPLETED!")