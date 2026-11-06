import yfinance as yf
import pandas as pd


def get_stock_data(stock="RELIANCE.NS"):

    print(f"\nDownloading intraday data for {stock}...")

    try:
        raw = yf.download(
            stock,
            period="5d",
            interval="5m",
            auto_adjust=True,
            progress=False,
            threads=False
        )

        if raw.empty:
            raise ValueError("No stock data received from Yahoo Finance.")

        # Handle multi-level columns
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)

        # Select required columns
        required_columns = ["Close", "Volume"]

        for column in required_columns:
            if column not in raw.columns:
                raise ValueError(f"Missing column: {column}")

        data = raw[required_columns].copy()

        # Clean data
        data.dropna(subset=["Close"], inplace=True)

        data["Close"] = pd.to_numeric(
            data["Close"], errors="coerce"
        )

        data["Volume"] = pd.to_numeric(
            data["Volume"], errors="coerce"
        )

        data.dropna(inplace=True)

        if data.empty:
            raise ValueError("No valid market data available.")

        if (data["Close"] <= 0).any():
            raise ValueError("Invalid stock prices detected.")

        print("Intraday data downloaded successfully!")
        print("Total records:", len(data))
        print("Latest candle:", data.index[-1])
        print("Latest price:", round(float(data["Close"].iloc[-1]), 2))

        return data

    except Exception as error:
        print("DATA DOWNLOAD ERROR:", error)
        raise


if __name__ == "__main__":

    stock_data = get_stock_data("RELIANCE.NS")

    print("\nLatest market data:")
    print(stock_data.tail(10))