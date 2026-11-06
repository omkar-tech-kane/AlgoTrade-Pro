import pandas as pd


def generate_signals(data):

    data = data.copy()

    # Moving averages
    data["SMA20"] = data["Close"].rolling(20).mean()

    data["SMA50"] = data["Close"].rolling(50).mean()

    # RSI calculation
    delta = data["Close"].diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1/14,
        adjust=False,
        min_periods=14
    ).mean()

    avg_loss = loss.ewm(
        alpha=1/14,
        adjust=False,
        min_periods=14
    ).mean()

    rs = avg_gain / avg_loss

    data["RSI"] = 100 - (100 / (1 + rs))

    data.loc[
        (avg_loss == 0) & (avg_gain > 0),
        "RSI"
    ] = 100

    data.loc[
        (avg_gain == 0) & (avg_loss == 0),
        "RSI"
    ] = 50

    # MACD calculation
    ema12 = data["Close"].ewm(
        span=12,
        adjust=False
    ).mean()

    ema26 = data["Close"].ewm(
        span=26,
        adjust=False
    ).mean()

    data["MACD"] = ema12 - ema26

    data["MACD_Signal"] = data["MACD"].ewm(
        span=9,
        adjust=False
    ).mean()

    data["MACD_Histogram"] = (
        data["MACD"] - data["MACD_Signal"]
    )

    # Existing SMA crossover strategy
    data["Signal"] = 0

    buy = (
        (data["SMA20"] > data["SMA50"]) &
        (data["SMA20"].shift(1) <= data["SMA50"].shift(1))
    )

    sell = (
        (data["SMA20"] < data["SMA50"]) &
        (data["SMA20"].shift(1) >= data["SMA50"].shift(1))
    )

    data.loc[buy, "Signal"] = 1

    data.loc[sell, "Signal"] = -1

    return data