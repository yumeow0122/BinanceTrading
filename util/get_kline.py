import os
import pandas as pd
from dotenv import load_dotenv
from binance.client import Client
from datetime import datetime

def fetch_data(symbols, start_date="2020-01-01", end_date="2024-12-31", interval=Client.KLINE_INTERVAL_1HOUR):
    load_dotenv()

    api_key = os.getenv("BINANCE_API_KEY")
    secret_key = os.getenv("BINANCE_SECRET_KEY")
    client = Client(api_key, secret_key)
    
    start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
    end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)

    for symbol in symbols:
        print(f"Fetching K-lines for {symbol}...")
        klines = client.get_historical_klines(symbol, interval, start_ts, end_ts)

        df = pd.DataFrame(klines, columns=[
            "Open Time", "Open", "High", "Low", "Close", "Volume",
            "Close Time", "Quote Asset Volume", "Number of Trades",
            "Taker Buy Base Volume", "Taker Buy Quote Volume", "Ignore"
        ])
        df.columns = [col.lower() for col in df.columns]

        df = df[["open", "high", "low", "close", "volume"]]

        filename = f"./data/{symbol}.csv"
        df.to_csv(filename, index=False)
        print(f"Saved K-lines for {symbol} to {filename}")

    print("All data fetched and saved!")
    
def main():
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    start_date = "2024-06-01"
    end_date = "2024-12-31"
    interval = Client.KLINE_INTERVAL_1HOUR
    fetch_data(symbols, start_date, end_date, interval)
    
if __name__ == "__main__":
    main()