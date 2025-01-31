import os
from datetime import datetime, timedelta

import pandas as pd
from dotenv import load_dotenv
from binance.client import Client

from .base import ExchangeAPI


class BinanceAPI(ExchangeAPI):
    def __init__(self, api_key: str, secret_key: str):
        self.client = Client(api_key, secret_key)

    def place_market_order(self, symbol: str, side: str, quantity: float) -> dict:
        """
        Place a market order on Binance
        
        :param symbol: trading pair, e.g. "BTCUSDT"
        :param side: "BUY" or "SELL"
        :param quantity: order quantity
        :return: order information returned by the exchange
        """
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type="MARKET",
                quantity=quantity
            )
            return order
        
        except Exception as e:
            print(f"❌ Binance Order Error: {e}")
            return {}

    def get_symbol_precision(self, symbol: str) -> int:
        """
        Get the precision of the trading pair on Binance
        
        :param symbol: trading pair, e.g. "BTCUSDT"
        :return: number of decimal places
        """
        try:
            exchange_info = self.client.futures_exchange_info()
            symbol_info = next(filter(lambda s: s["symbol"] == symbol, exchange_info["symbols"]))
            quantity_precision = symbol_info["quantityPrecision"]
            return quantity_precision
        
        except Exception as e:
            print(f"❌ Binance Data Error: {e}")
            return 0
        
    def fetch_historical_data(self, symbol: str, interval: str, days: int) -> pd.DataFrame:
        """
        Fetch historical K-line data from Binance
        
        :param symbol: trading pair, e.g. "BTCUSDT"
        :param interval: K-line interval, e.g. "1m, 5m, 15m, 1h, 4h, 1d"
        :param days: how many days of historical data to fetch
        :return: Pandas DataFrame containing K-line data
        """
        try:
            interval_mapping = {
                "1m": Client.KLINE_INTERVAL_1MINUTE,
                "5m": Client.KLINE_INTERVAL_5MINUTE,
                "15m": Client.KLINE_INTERVAL_15MINUTE,
                "1h": Client.KLINE_INTERVAL_1HOUR,
                "4h": Client.KLINE_INTERVAL_4HOUR,
                "1d": Client.KLINE_INTERVAL_1DAY,
            }
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)

            klines = self.client.get_historical_klines(
                symbol,
                interval_mapping.get(interval, Client.KLINE_INTERVAL_1HOUR),
                start_time.strftime("%Y-%m-%d %H:%M:%S"),
                end_time.strftime("%Y-%m-%d %H:%M:%S"),
            )

            df = pd.DataFrame(klines, columns=[
                "Open Time", "Open", "High", "Low", "Close", "Volume",
                "Close Time", "Quote Asset Volume", "Number of Trades",
                "Taker Buy Base Volume", "Taker Buy Quote Volume", "Ignore"
            ])
            df = df[["Open", "High", "Low", "Close", "Volume"]]
            df.columns = [col.lower() for col in df.columns]
            df = df.astype(float)
            return df
        
        except Exception as e:
            print(f"❌ Binance Data Error: {e}")
            return pd.DataFrame()
        
if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY")
    secret_key = os.getenv("BINANCE_SECRET_KEY")
    api = BinanceAPI(api_key, secret_key)
    
    binance_api = BinanceAPI(api_key, secret_key)
    historical_data = binance_api.fetch_historical_data("BTCUSDT", "1h", 1)
    print(historical_data.head())