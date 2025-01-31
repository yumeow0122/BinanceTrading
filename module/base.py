from abc import ABC, abstractmethod

import pandas as pd

class Notifier(ABC):
    """
    Notifier abstract base class, ensuring all notifier implementations have a unified interface
    """
    @abstractmethod
    def send_message(self, msg: str):
        pass

class ExchangeAPI(ABC):
    """
    ExchangeAPI abstract base class, ensuring all exchange API implementations have a unified interface
    """

    @abstractmethod
    def place_market_order(self, symbol: str, side: str, quantity: float) -> dict:
        """
        Send a market order to the exchange
        
        :param symbol: trading pair, e.g. "BTCUSDT"
        :param side: "BUY" or "SELL"
        :param quantity: order quantity
        :return: order information returned by the exchange
        """
        pass

    @abstractmethod
    def fetch_historical_data(self, symbol: str, interval: str, days: int) -> pd.DataFrame:
        """
        Fetch historical K-line data for previous days
        
        :param symbol: trading pair, e.g. "BTCUSDT"
        :param interval: K-line interval, e.g. "1h"
        :param days: how many days of historical data to fetch
        :return: Pandas DataFrame containing K-line data
        """
        pass