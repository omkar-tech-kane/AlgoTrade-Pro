import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from backtesting import run_backtest
from streamlit_autorefresh import st_autorefresh

from data_check import get_stock_data
from strategy import generate_signals
from paper_trading import simulate_trading, load_portfolio


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Algo Trading Dashboard",
    page_icon="📈",
    layout="wide"
)
# ==========================================
# PROFESSIONAL DASHBOARD DESIGN
# ==========================================

st.markdown("""
<style>

/* MAIN BACKGROUND */
.stApp {
    background: linear-gradient(135deg, #0b1120, #111827);
    color: #f1f5f9;
}

/* MAIN CONTENT */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

/* HEADINGS */
h1, h2, h3 {
    color: #f8fafc !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px;
}

/* PARAGRAPHS */
p, label {
    color: #cbd5e1;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #263449;
}

/* METRIC CARDS */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #1e293b, #172033);
    border: 1px solid #334155;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    transition: 0.2s ease;
}

div[data-testid="stMetric"]:hover {
    border-color: #38bdf8;
    transform: translateY(-3px);
}

div[data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
}

div[data-testid="stMetricValue"] {
    color: #f8fafc !important;
    font-weight: 700;
}

/* BUTTONS */
.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(90deg, #2563eb, #0891b2);
    color: white;
    border: none;
    border-radius: 9px;
    padding: 10px 20px;
    font-weight: 600;
    transition: 0.2s ease;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: linear-gradient(90deg, #1d4ed8, #0e7490);
    border: none;
    color: white;
}

/* INPUT FIELDS */
.stTextInput input,
.stSelectbox div[data-baseweb="select"] {
    background: #1e293b;
    color: white;
    border-radius: 8px;
}

/* DATA TABLES */
div[data-testid="stDataFrame"] {
    border: 1px solid #334155;
    border-radius: 12px;
    overflow: hidden;
}

/* ALERT BOXES */
div[data-testid="stAlert"] {
    border-radius: 12px;
    border: 1px solid #334155;
}

/* SECTION DIVIDERS */
hr {
    border-color: #334155;
    margin-top: 25px;
    margin-bottom: 25px;
}

/* EXPANDERS */
div[data-testid="stExpander"] {
    background: #172033;
    border: 1px solid #334155;
    border-radius: 12px;
}

/* CAPTIONS */
.stCaption {
    color: #94a3b8 !important;
}

/* HIDE STREAMLIT BRANDING */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)
st.markdown("""
<div style="
    background: linear-gradient(110deg, #1d4ed8, #0891b2);
    padding: 30px;
    border-radius: 18px;
    margin-bottom: 25px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.25);
">
    <h1 style="color:white; margin:0; font-size:36px;">
        📈 AlgoTrade Pro
    </h1>
    <p style="color:#e0f2fe; margin:8px 0 0 0; font-size:16px;">
        Intelligent Market Analytics | Technical Indicators |
        Paper Trading
    </p>
    <p style="color:#dbeafe; margin:8px 0 0 0; font-size:12px;">
        EDUCATIONAL SIMULATION • MARKET DATA • STRATEGY ANALYSIS
    </p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# AUTO REFRESH
# --------------------------------------------------

st_autorefresh(
    interval=30000,
    key="dashboard_refresh"
)


# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

@st.cache_data(ttl=30)
def load_data(symbol):
    data = get_stock_data(symbol)

    if data.empty:
        raise ValueError("No market data available.")

    return data


# --------------------------------------------------
# WATCHLIST INITIALIZATION
# --------------------------------------------------

if "watchlist" not in st.session_state:
    st.session_state.watchlist = [
        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
        "AAPL"
    ]


# --------------------------------------------------
# SIDEBAR: STOCK SEARCH
# --------------------------------------------------

st.sidebar.header("🔍 Stock Search")

with st.sidebar.form("stock_search_form"):
    stock = st.text_input(
        "Enter Yahoo Finance ticker",
        value="RELIANCE.NS"
    ).strip().upper()

    search_button = st.form_submit_button("Search Stock")

if not stock:
    stock = "RELIANCE.NS"

if stock not in st.session_state.watchlist:
    st.session_state.watchlist.append(stock)


# --------------------------------------------------
# SIDEBAR: WATCHLIST MANAGEMENT
# --------------------------------------------------

st.sidebar.divider()
st.sidebar.header("⭐ Watchlist")

with st.sidebar.form("add_watchlist_form"):
    new_symbol = st.text_input("Add ticker symbol")
    add_button = st.form_submit_button("Add to Watchlist")

if add_button:
    new_symbol = new_symbol.strip().upper()

    if new_symbol and new_symbol not in st.session_state.watchlist:
        st.session_state.watchlist.append(new_symbol)
        st.sidebar.success(f"{new_symbol} added.")
        st.rerun()

if st.session_state.watchlist:
    remove_symbol = st.sidebar.selectbox(
        "Select ticker to remove",
        st.session_state.watchlist
    )

    if st.sidebar.button("Remove from Watchlist"):
        st.session_state.watchlist.remove(remove_symbol)
        st.rerun()


# --------------------------------------------------
# LOAD SELECTED STOCK
# --------------------------------------------------

try:
    raw_data = load_data(stock)
    results = generate_signals(raw_data)

    results, trades = simulate_trading(
        results,
        symbol=stock,
        persistent=True
    )

    portfolio = load_portfolio(stock)

except Exception as error:
    st.error(f"Unable to load {stock}: {error}")
    st.info("Check the ticker symbol and try again.")
    st.stop()


# --------------------------------------------------
# MARKET DATA STATUS
# --------------------------------------------------

st.subheader("📡 Market Data Status")

latest_price = float(results["Close"].iloc[-1])
latest_timestamp = pd.Timestamp(results.index[-1])

if latest_timestamp.tzinfo is not None:
    current_time = pd.Timestamp.now(tz=latest_timestamp.tz)
else:
    current_time = pd.Timestamp.now()

data_age = current_time - latest_timestamp

status_col1, status_col2, status_col3 = st.columns(3)

status_col1.metric(
    "Selected Stock",
    stock
)

status_col2.metric(
    "Latest Available Price",
    f"₹{latest_price:,.2f}"
)

status_col3.metric(
    "Latest Candle",
    latest_timestamp.strftime("%d-%m-%Y %H:%M")
)

st.caption(
    f"Data age: {data_age}. "
    "Yahoo Finance data may be delayed or incomplete. "
    "Refreshing the dashboard does not guarantee a new market price."
)


# --------------------------------------------------
# PORTFOLIO CALCULATIONS
# --------------------------------------------------

cash = float(portfolio["cash"])
shares = int(portfolio["shares"])
entry_price = float(portfolio["entry_price"])
position_cost = float(portfolio["position_cost"])

portfolio_value = cash + (shares * latest_price)

unrealized_pnl = (
    shares * latest_price - position_cost
    if shares > 0
    else 0.0
)

realized_pnl = sum(
    float(trade.get("Realized_PnL", 0))
    for trade in portfolio["trades"]
    if trade.get("Action") == "SELL"
)

total_pnl = portfolio_value - 100000

total_return = (total_pnl / 100000) * 100


# --------------------------------------------------
# PORTFOLIO OVERVIEW
# --------------------------------------------------

st.divider()
st.subheader("💼 Paper Trading Portfolio")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Available Cash",
    f"₹{cash:,.2f}"
)

col2.metric(
    "Portfolio Value",
    f"₹{portfolio_value:,.2f}"
)

col3.metric(
    "Total P/L",
    f"₹{total_pnl:,.2f}",
    f"{total_return:.2f}%"
)

col4, col5, col6 = st.columns(3)

col4.metric(
    "Current Holdings",
    shares
)

col5.metric(
    "Average Entry Price",
    f"₹{entry_price:,.2f}" if shares > 0 else "N/A"
)

col6.metric(
    "Unrealized P/L",
    f"₹{unrealized_pnl:,.2f}"
)

col7, col8 = st.columns(2)

col7.metric(
    "Realized P/L",
    f"₹{realized_pnl:,.2f}"
)

col8.metric(
    "Total Transactions",
    len(portfolio["trades"])
)


# --------------------------------------------------
# LATEST MARKET SIGNAL
# --------------------------------------------------

st.divider()
st.subheader("📊 Latest Market Signal")

latest_signal = results["Signal"].iloc[-1]

if pd.isna(latest_signal):
    latest_signal = 0
else:
    latest_signal = int(latest_signal)

signal_col1, signal_col2, signal_col3 = st.columns(3)

if latest_signal == 1:
    signal_col1.success("BUY crossover detected")

elif latest_signal == -1:
    signal_col1.error("SELL crossover detected")

else:
    signal_col1.info("No new crossover detected")


sma20 = results["SMA20"].iloc[-1]
sma50 = results["SMA50"].iloc[-1]

if pd.notna(sma20) and pd.notna(sma50):

    if sma20 > sma50:
        signal_col2.success("Bullish SMA alignment")

    elif sma20 < sma50:
        signal_col2.warning("Bearish SMA alignment")

    else:
        signal_col2.info("SMA values are equal")


rsi = results["RSI"].iloc[-1]

if pd.notna(rsi):
    signal_col3.metric("RSI", f"{rsi:.2f}")


st.caption(
    "Signals are based on SMA20/SMA50 crossover events. "
    "RSI and MACD are supporting indicators, not independent trade triggers."
)

# --------------------------------------------------
# CONTINUOUS MARKET STATUS
# --------------------------------------------------

st.divider()
st.subheader(f"📊 Market Status: {stock}")

latest = results.iloc[-1]

sma20 = latest["SMA20"]
sma50 = latest["SMA50"]
rsi = latest["RSI"]
macd = latest["MACD"]
macd_signal = latest["MACD_Signal"]

if all(pd.notna(x) for x in [sma20, sma50, rsi, macd, macd_signal]):

    bullish_points = 0
    bearish_points = 0

    # SMA TREND
    if sma20 > sma50:
        bullish_points += 1
    elif sma20 < sma50:
        bearish_points += 1

    # RSI MOMENTUM
    if rsi > 50:
        bullish_points += 1
    elif rsi < 50:
        bearish_points += 1

    # MACD MOMENTUM
    if macd > macd_signal:
        bullish_points += 1
    elif macd < macd_signal:
        bearish_points += 1

    # FINAL STATUS
    if bullish_points >= 2:
        market_status = "PAPER BUY SETUP"
        status_message = "Bullish indicator confirmation"
    
    elif bearish_points >= 2:
        market_status = "PAPER SELL SETUP"
        status_message = "Bearish indicator confirmation"

    else:
        market_status = "HOLD"
        status_message = "Mixed market indicators"

    # DISPLAY STATUS
    if market_status == "PAPER BUY SETUP":
        st.success(f"🟢 {market_status}")

    elif market_status == "PAPER SELL SETUP":
        st.error(f"🔴 {market_status}")

    else:
        st.warning(f"🟡 {market_status}")

    c1, c2, c3 = st.columns(3)

    c1.metric("Bullish Indicators", bullish_points)
    c2.metric("Bearish Indicators", bearish_points)
    c3.metric("RSI", f"{rsi:.2f}")

    st.write(f"**Analysis:** {status_message}")

else:
    st.warning("Insufficient indicator data. Waiting for more candles.")

st.caption(
    "Educational indicator-based signals only. "
    "These statuses do not guarantee future price movements. "
    "The paper-trading simulator still executes using SMA crossover signals."
)

# --------------------------------------------------
# STOCK PRICE CHART
# --------------------------------------------------

st.divider()
st.subheader("📈 Stock Price Chart")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=results.index,
        y=results["Close"],
        name="Close Price",
        line=dict(width=2)
    )
)

fig.add_trace(
    go.Scatter(
        x=results.index,
        y=results["SMA20"],
        name="SMA 20"
    )
)

fig.add_trace(
    go.Scatter(
        x=results.index,
        y=results["SMA50"],
        name="SMA 50"
    )
)

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Price",
    hovermode="x unified",
    height=500
)

st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# RSI CHART
# --------------------------------------------------

st.subheader("📉 Relative Strength Index")

rsi_fig = go.Figure()

rsi_fig.add_trace(
    go.Scatter(
        x=results.index,
        y=results["RSI"],
        name="RSI",
        line=dict(width=2)
    )
)

rsi_fig.add_hline(y=70, line_dash="dash")
rsi_fig.add_hline(y=30, line_dash="dash")

rsi_fig.update_layout(
    yaxis_title="RSI",
    height=300
)

st.plotly_chart(rsi_fig, use_container_width=True)


# --------------------------------------------------
# MACD CHART
# --------------------------------------------------

st.subheader("📊 MACD Indicator")

macd_fig = go.Figure()

macd_fig.add_trace(
    go.Scatter(
        x=results.index,
        y=results["MACD"],
        name="MACD"
    )
)

macd_fig.add_trace(
    go.Scatter(
        x=results.index,
        y=results["MACD_Signal"],
        name="Signal Line"
    )
)

macd_fig.add_trace(
    go.Bar(
        x=results.index,
        y=results["MACD_Histogram"],
        name="Histogram"
    )
)

macd_fig.update_layout(height=350)

st.plotly_chart(macd_fig, use_container_width=True)


# --------------------------------------------------
# PORTFOLIO EQUITY HISTORY
# --------------------------------------------------

st.divider()
st.subheader("💰 Portfolio Equity History")

equity_history = portfolio.get("equity_history", {})

if equity_history:

    equity_df = pd.DataFrame(
        list(equity_history.items()),
        columns=["Timestamp", "Portfolio Value"]
    )

    equity_df["Timestamp"] = pd.to_datetime(
        equity_df["Timestamp"],
        utc=True
    )

    equity_df = equity_df.sort_values("Timestamp")

    equity_fig = go.Figure()

    equity_fig.add_trace(
        go.Scatter(
            x=equity_df["Timestamp"],
            y=equity_df["Portfolio Value"],
            name="Portfolio Value",
            mode="lines"
        )
    )

    equity_fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Portfolio Value (₹)",
        height=350
    )

    st.plotly_chart(
        equity_fig,
        use_container_width=True
    )

else:
    st.info("Portfolio equity history will appear after candles are processed.")


# --------------------------------------------------
# TRADE HISTORY
# --------------------------------------------------

st.divider()
st.subheader("📜 Paper Trading History")

if portfolio["trades"]:

    trade_df = pd.DataFrame(portfolio["trades"])

    trade_df["Date"] = pd.to_datetime(
        trade_df["Date"],
        errors="coerce"
    )

    st.dataframe(
        trade_df.sort_values("Date", ascending=False),
        use_container_width=True
    )

else:
    st.info("No paper trades have been executed yet.")

# --------------------------------------------------
# PORTFOLIO PERFORMANCE ANALYTICS
# --------------------------------------------------

st.divider()
st.subheader("📊 Portfolio Performance Analytics")

all_trades = portfolio.get("trades", [])

# Only SELL transactions represent completed trades
closed_trades = [
    trade for trade in all_trades
    if trade.get("Action") == "SELL"
]

winning_trades = [
    trade for trade in closed_trades
    if float(trade.get("Realized_PnL", 0)) > 0
]

losing_trades = [
    trade for trade in closed_trades
    if float(trade.get("Realized_PnL", 0)) < 0
]

total_closed = len(closed_trades)

win_rate = (
    len(winning_trades) / total_closed * 100
    if total_closed > 0 else 0
)

gross_profit = sum(
    float(trade["Realized_PnL"])
    for trade in winning_trades
)

gross_loss = abs(sum(
    float(trade["Realized_PnL"])
    for trade in losing_trades
))

profit_factor = (
    gross_profit / gross_loss
    if gross_loss > 0 else None
)

# Maximum drawdown
equity_values = list(
    portfolio.get("equity_history", {}).values()
)

if equity_values:
    equity_series = pd.Series(
        equity_values,
        dtype=float
    )

    running_peak = equity_series.cummax()

    drawdown = (
        (equity_series - running_peak) / running_peak
    ) * 100

    max_drawdown = abs(float(drawdown.min()))

else:
    max_drawdown = 0.0


# Performance metrics
st.markdown("### Trading Statistics")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Win Rate",
    f"{win_rate:.2f}%"
)

c2.metric(
    "Winning Trades",
    len(winning_trades)
)

c3.metric(
    "Losing Trades",
    len(losing_trades)
)

c4, c5, c6 = st.columns(3)

c4.metric(
    "Gross Profit",
    f"₹{gross_profit:,.2f}"
)

c5.metric(
    "Gross Loss",
    f"₹{gross_loss:,.2f}"
)

c6.metric(
    "Profit Factor",
    f"{profit_factor:.2f}"
    if profit_factor is not None
    else "N/A"
)

st.metric(
    "Maximum Drawdown",
    f"{max_drawdown:.2f}%"
)


# Realized P/L chart
st.markdown("### Completed Trade P/L")

if closed_trades:

    pnl_df = pd.DataFrame(closed_trades)

    pnl_df["Trade Number"] = range(
        1, len(pnl_df) + 1
    )

    pnl_fig = go.Figure()

    pnl_fig.add_trace(
        go.Bar(
            x=pnl_df["Trade Number"],
            y=pnl_df["Realized_PnL"],
            name="Realized P/L"
        )
    )

    pnl_fig.add_hline(y=0, line_dash="dash")

    pnl_fig.update_layout(
        xaxis_title="Completed Trade",
        yaxis_title="Realized P/L (₹)",
        height=350
    )

    st.plotly_chart(
        pnl_fig,
        use_container_width=True
    )

else:
    st.info(
        "Performance statistics will appear after completed paper trades."
    )
# --------------------------------------------------
# HISTORICAL BACKTESTING ENGINE
# --------------------------------------------------

st.divider()
st.subheader("🧪 Historical Strategy Backtesting")

st.write(
    "Test your SMA20/SMA50 strategy using the selected "
    "stock's available historical market data."
)

if st.button("▶ Run Historical Backtest", key="run_backtest"):

    try:
        with st.spinner("Running historical backtest..."):

            backtest_equity, backtest_trades, backtest_metrics = (
                run_backtest(results)
            )

            st.session_state.backtest_equity = backtest_equity
            st.session_state.backtest_trades = backtest_trades
            st.session_state.backtest_metrics = backtest_metrics
            st.session_state.backtest_stock = stock

        st.success("Backtest completed successfully!")

    except Exception as error:
        st.error(f"Backtesting error: {error}")


# Display saved results
if (
    "backtest_metrics" in st.session_state
    and st.session_state.backtest_stock == stock
):

    metrics = st.session_state.backtest_metrics

    st.markdown("### Backtest Results")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Initial Capital",
        f"₹{metrics['Initial Capital']:,.2f}"
    )

    c2.metric(
        "Final Capital",
        f"₹{metrics['Final Capital']:,.2f}"
    )

    c3.metric(
        "Total Return",
        f"{metrics['Total Return (%)']:.2f}%"
    )

    c4, c5, c6 = st.columns(3)

    c4.metric(
        "Total Trades",
        metrics["Total Trades"]
    )

    c5.metric(
        "Win Rate",
        f"{metrics['Win Rate (%)']:.2f}%"
    )

    c6.metric(
        "Maximum Drawdown",
        f"{metrics['Maximum Drawdown (%)']:.2f}%"
    )

    st.markdown("### Trade Statistics")

    st.write(
        f"Winning Trades: {metrics['Winning Trades']}"
    )

    st.write(
        f"Losing Trades: {metrics['Losing Trades']}"
    )

    # Equity curve
    equity = st.session_state.backtest_equity

    if not equity.empty:

        equity_chart = go.Figure()

        equity_chart.add_trace(
            go.Scatter(
                x=equity["Date"],
                y=equity["Portfolio_Value"],
                mode="lines",
                name="Backtest Portfolio Value"
            )
        )

        equity_chart.update_layout(
            title="Historical Backtest Equity Curve",
            xaxis_title="Date",
            yaxis_title="Portfolio Value (₹)",
            height=400
        )

        st.plotly_chart(
            equity_chart,
            use_container_width=True
        )

    # Backtest trade history
    backtest_trades = st.session_state.backtest_trades

    if backtest_trades:

        st.markdown("### Backtest Trade History")

        backtest_df = pd.DataFrame(backtest_trades)

        st.dataframe(
            backtest_df,
            use_container_width=True
        )

    else:
        st.info("No trades were generated during this backtest.")

else:
    st.info("Click the button above to run your first historical backtest.")    
# --------------------------------------------------
# WATCHLIST MARKET MONITOR
# --------------------------------------------------

st.divider()
st.subheader("⭐ Watchlist Market Monitor")

watchlist_data = []

for symbol in st.session_state.watchlist:

    try:

        if symbol == stock:
            monitor_data = results

        else:
            monitor_raw = load_data(symbol)
            monitor_data = generate_signals(monitor_raw)

        price = float(monitor_data["Close"].iloc[-1])

        signal = monitor_data["Signal"].iloc[-1]
        rsi_value = monitor_data["RSI"].iloc[-1]

        sma20_value = monitor_data["SMA20"].iloc[-1]
        sma50_value = monitor_data["SMA50"].iloc[-1]

        if pd.isna(signal):
            signal_text = "HOLD"
        elif signal == 1:
            signal_text = "BUY SIGNAL"
        elif signal == -1:
            signal_text = "SELL SIGNAL"
        else:
            signal_text = "HOLD"

        if pd.notna(sma20_value) and pd.notna(sma50_value):

            if sma20_value > sma50_value:
                trend = "Bullish"

            elif sma20_value < sma50_value:
                trend = "Bearish"

            else:
                trend = "Neutral"

        else:
            trend = "Insufficient Data"

        watchlist_data.append({
            "Stock": symbol,
            "Price": round(price, 2),
            "Signal": signal_text,
            "Trend": trend,
            "RSI": round(rsi_value, 2)
            if pd.notna(rsi_value)
            else None
        })

    except Exception as error:

        watchlist_data.append({
            "Stock": symbol,
            "Price": "N/A",
            "Signal": "Data Error",
            "Trend": str(error),
            "RSI": "N/A"
        })


watchlist_df = pd.DataFrame(watchlist_data)

st.dataframe(
    watchlist_df,
    use_container_width=True
)


# --------------------------------------------------
# MARKET SIGNAL ALERTS
# --------------------------------------------------

st.subheader("🔔 Market Signal Alerts")

alerts_found = False

for item in watchlist_data:

    symbol_name = item["Stock"]
    signal_text = item["Signal"]
    rsi_value = item["RSI"]

    if signal_text == "BUY SIGNAL":

        st.success(
            f"{symbol_name}: New BUY crossover detected."
        )

        alerts_found = True

    elif signal_text == "SELL SIGNAL":

        st.error(
            f"{symbol_name}: New SELL crossover detected."
        )

        alerts_found = True

    if isinstance(rsi_value, (int, float)):

        if rsi_value > 70:

            st.warning(
                f"{symbol_name}: RSI is above 70."
            )

            alerts_found = True

        elif rsi_value < 30:

            st.info(
                f"{symbol_name}: RSI is below 30."
            )

            alerts_found = True


if not alerts_found:
    st.info("No current watchlist alerts.")


st.caption(
    "These are dashboard alerts, not push notifications. "
    "They may remain visible until the market data changes."
)


# --------------------------------------------------
# HISTORICAL DATA
# --------------------------------------------------

st.divider()

with st.expander("View Historical Market Data"):

    st.dataframe(
        results.tail(100),
        use_container_width=True
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Educational paper-trading project. "
    "No real orders are placed. "
    "Market data is provided by Yahoo Finance and may be delayed."
)
st.html("""
<style>
.algo-footer {
    background: linear-gradient(135deg, #0f172a, #172554);
    color: #e2e8f0;
    padding: 40px 25px 25px;
    margin-top: 50px;
    border: 1px solid #334155;
    border-radius: 15px;
    text-align: center;
    font-family: Arial, sans-serif;
}

.algo-footer h2 {
    color: #38bdf8;
    font-size: 28px;
}

.algo-footer h3 {
    color: #38bdf8;
}

.algo-footer p {
    line-height: 1.8;
}

.algo-footer hr {
    border: 0;
    border-top: 1px solid #475569;
    margin: 25px auto;
    max-width: 750px;
}

.developer {
    font-size: 22px;
    font-weight: bold;
    color: white;
}

.email {
    color: #38bdf8;
    text-decoration: none;
}

.disclaimer, .project-note {
    background: #1e293b;
    border: 1px solid #475569;
    border-radius: 10px;
    padding: 20px;
    margin: 25px auto;
    max-width: 950px;
    text-align: left;
    font-size: 13px;
    color: #cbd5e1;
}

.disclaimer h3, .project-note h3 {
    text-align: center;
}

.quote {
    margin: 35px auto 20px;
    max-width: 850px;
    font-size: 19px;
    font-weight: bold;
    font-style: italic;
    color: #ffffff;
}

.credit, .copyright {
    color: #94a3b8;
    font-size: 12px;
}
</style>

<div class="algo-footer">

    <h2>⚡ AlgoTrade Pro</h2>

    <p>Educational Algorithmic Trading & Paper Trading Dashboard</p>

    <hr>

    <h3>👨‍💻 Designed & Developed by</h3>

    <p class="developer">Omkar Vasant Kane</p>

    <p>
        📧 <a class="email"
        href="mailto:officialomkar2008@gmail.com">
        officialomkar2008@gmail.com</a>
    </p>

    <div class="disclaimer">

        <h3>⚠️ IMPORTANT DISCLAIMER</h3>

        This platform is developed strictly for educational,
        learning and research purposes only.

        <br><br>

        AlgoTrade Pro is a paper trading and historical
        backtesting project. It does not execute real trades
        or provide personalized financial or investment advice.

        <br><br>

        All trading signals, strategies, indicators and
        simulated results are for demonstration purposes only.
        Historical performance does not guarantee future results.

        <br><br>

        Market data from third-party sources may be delayed,
        incomplete or inaccurate.

        <br><br>

        Do not make financial or investment decisions based
        solely on this platform.

    </div>

    <div class="project-note">

        <h3>📘 ABOUT THIS PROJECT</h3>

        <p>
        AlgoTrade Pro is a basic educational project developed
        to enhance programming, problem-solving, analytical
        thinking and technical skills through practical learning.
        </p>

        <p>
        This project represents a learning journey in Python,
        financial data analysis, algorithmic strategies and
        dashboard development.
        </p>

    </div>

    <div class="quote">

        <h3>💡 KEEP LEARNING, KEEP BUILDING</h3>

        "Great things are built one step at a time.
        Keep learning, keep improving, and never stop creating."

    </div>

    <p class="credit">
        Developed with guidance and coding assistance from ChatGPT.
    </p>

    <p class="copyright">
        © 2026 AlgoTrade Pro. All Rights Reserved.
    </p>

</div>
""")