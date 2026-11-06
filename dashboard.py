import matplotlib.pyplot as plt

from data_check import get_stock_data
from strategy import generate_signals
from paper_trading import simulate_trading


# =====================================
# PROJECT SETTINGS
# =====================================

STOCK = "RELIANCE.NS"

INITIAL_CAPITAL = 100000


# =====================================
# DOWNLOAD DATA
# =====================================

print("Loading Trading Dashboard...")

data = get_stock_data(STOCK)

data = generate_signals(data)


# =====================================
# RUN PAPER TRADING
# =====================================

results, trades = simulate_trading(data)


# =====================================
# CALCULATE STATISTICS
# =====================================

latest_price = float(results["Close"].iloc[-1])

final_value = float(results["Equity"].iloc[-1])

profit = final_value - INITIAL_CAPITAL

returns = (profit / INITIAL_CAPITAL) * 100

peak = results["Equity"].cummax()

drawdown = (
    (results["Equity"] - peak) / peak
)

max_drawdown = abs(drawdown.min()) * 100

closed_trades = [
    t for t in trades
    if t["Action"] == "SELL"
]

winning_trades = sum(
    t["Realized_PnL"] > 0
    for t in closed_trades
)

total_trades = len(closed_trades)

win_rate = (
    winning_trades / total_trades * 100
    if total_trades > 0 else 0
)


# =====================================
# CREATE DASHBOARD
# =====================================

fig, axes = plt.subplots(
    3, 1,
    figsize=(14, 12)
)

fig.suptitle(
    "ALGO TRADING BOT - PAPER TRADING DASHBOARD",
    fontsize=16,
    fontweight="bold"
)


# =====================================
# CHART 1: STOCK PRICE
# =====================================

ax = axes[0]

ax.plot(
    results.index,
    results["Close"],
    label="Stock Price",
    linewidth=1.5
)

ax.plot(
    results.index,
    results["SMA20"],
    label="SMA 20",
    linewidth=1
)

ax.plot(
    results.index,
    results["SMA50"],
    label="SMA 50",
    linewidth=1
)

buys = results[
    results["Executed_Action"] == "BUY"
]

sells = results[
    results["Executed_Action"] == "SELL"
]

ax.scatter(
    buys.index,
    buys["Close"],
    marker="^",
    label="BUY",
    s=80
)

ax.scatter(
    sells.index,
    sells["Close"],
    marker="v",
    label="SELL",
    s=80
)

ax.set_title(f"{STOCK} - Price and Trading Signals")

ax.set_ylabel("Price (INR)")

ax.legend()

ax.grid(True)


# =====================================
# CHART 2: PORTFOLIO PERFORMANCE
# =====================================

ax = axes[1]

ax.plot(
    results.index,
    results["Equity"],
    label="Portfolio Value",
    linewidth=2
)

ax.axhline(
    INITIAL_CAPITAL,
    linestyle="--",
    label="Initial Capital"
)

ax.set_title("Portfolio Performance")

ax.set_ylabel("Portfolio Value (INR)")

ax.legend()

ax.grid(True)


# =====================================
# CHART 3: DRAWDOWN
# =====================================

ax = axes[2]

ax.plot(
    results.index,
    drawdown * 100,
    label="Drawdown (%)"
)

ax.set_title("Portfolio Drawdown")

ax.set_ylabel("Drawdown (%)")

ax.set_xlabel("Date")

ax.legend()

ax.grid(True)


# =====================================
# DISPLAY SUMMARY
# =====================================

summary = (
    f"Latest Price: Rs. {latest_price:,.2f}    |    "
    f"Portfolio: Rs. {final_value:,.2f}    |    "
    f"P/L: Rs. {profit:,.2f}    |    "
    f"Return: {returns:.2f}%    |    "
    f"Max Drawdown: {max_drawdown:.2f}%    |    "
    f"Win Rate: {win_rate:.2f}%    |    "
    f"Closed Trades: {total_trades}"
)

fig.text(
    0.5,
    0.015,
    summary,
    ha="center",
    fontsize=9
)

plt.tight_layout(rect=[0, 0.06, 1, 0.95])


# =====================================
# SAVE DASHBOARD
# =====================================

plt.savefig(
    "reports/trading_dashboard.png",
    dpi=150
)

print("\nDashboard saved successfully!")

print("Location: reports/trading_dashboard.png")


# =====================================
# DISPLAY DASHBOARD
# =====================================

plt.show()