import os
import time
import logging
from dotenv import load_dotenv

import pandas as pd
from datetime import datetime, timedelta

from module.BinanceAPI import BinanceAPI
from module.PortfolioManager import PortfolioManager
from module.TelegramNotifier import TelegramNotifier

class TradingAgent:
    def __init__(self, exchange_api, portfolio_manager, notifier, symbol="BTCUSDT"):
        """
        Trading Agent class to manage trading operations for specific symbol.
        
        :param exchange_api: BinanceAPI object
        :param portfolio_manager: PortfolioManager object
        :param notifier: TelegramNotifier object
        :param symbol: Trading symbol
        """
        self.exchange_api = exchange_api
        self.portfolio_manager = portfolio_manager
        self.notifier = notifier
        self.symbol = symbol
        self.trades = []
        
        logging.basicConfig(
            filename=f"logs/{symbol}.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        self.logger = logging.getLogger(__name__)
        
        try:
            self.exchange_api.client.futures_change_leverage(symbol=self.symbol, leverage=self.portfolio_manager.leverage)
            self.exchange_api.client.futures_change_margin_type(symbol=self.symbol, marginType="ISOLATED")
        except Exception as e:
            print(f"❌ Error setting leverage for {self.symbol}: {e}")
        
    def open_long(self, price, size=None):
        """
        Open long position with given price at binance futures with leverage and isolated margin type.
        
        :param price: Price to open long position
        :param size: Size of position, if None, calculate position based on all capital
        
        :return: None
        """
        position = self.portfolio_manager.calculate_position(price, size)
        self.portfolio_manager.update_balance(position, price, "open")
        self.trades.append({"type": "open", "side": "BUY", "price": price, "size": position})
        
        trade_msg = f"📉 Opened Long position:\nSymbol: {self.symbol}\nPrice: {price}\nSize: {position:.6f}"
        self.notifier.send_message(trade_msg)
        self.logger.info(f"Opened LONG | Symbol: {self.symbol} | Price: {price} | Size: {position:.6f}")

    def open_short(self, price, size=None):
        """
        Open short position with given price at binance futures with leverage and isolated margin type.
        
        :param price: Price to open short position
        :param size: Size of position, if None, calculate position based on all capital
        
        :return: None
        """
        position = self.portfolio_manager.calculate_position(price, size)
        self.portfolio_manager.update_balance(-position, price, "open")
        self.trades.append({"type": "open", "side": "SELL", "price": price, "size": position})
        
        trade_msg = f"📉 Opened SHORT position:\nSymbol: {self.symbol}\nPrice: {price}\nSize: {position:.6f}"
        self.notifier.send_message(trade_msg)
        self.logger.info(f"Opened SHORT | Symbol: {self.symbol} | Price: {price} | Size: {position:.6f}")

    def close_position(self, price):
        """
        Close current position with given price at binance futures.
        
        :param price: Price to close position

        :return: None
        """
        position = self.portfolio_manager.position
        side = "SELL" if position > 0 else "BUY"
        gain = self.portfolio_manager.update_balance(position, price, "close")
        self.trades.append({"type": "close", "side": side, "price": price, "size": abs(position)})
        
        action = '📉 Closed LONG' if self.position > 0 else '📈 Closed SHORT'
        trade_msg = f"{action} position:\nSymbol: {self.symbol}\nPrice: {price}\nGain: {gain:.2f}"
        self.notifier.send_message(trade_msg)
        self.logger.info(f"Closed {side} | Symbol: {self.symbol} | Price: {price} | Gain: {gain:.2f}")

    def fetch_historical_data(self, interval, days):
        """
        fetch historical data for given symbol and interval.
        
        :param interval: Interval of data (1m, 5m, 15m, 1h, 4h, 1d)
        :param days: Number of days to fetch historical data
        
        :return: DataFrame of historical data
        """
        return self.exchange_api.fetch_historical_data(self.symbol, interval, days)

    def get_status(self, price):
        """
        Get current status of trading agent.
        
        :param price: Current price of symbol
        
        :return: Dictionary of status
        """
        return self.portfolio_manager.get_status(price)

    def analyze(self, historical_data):
        """
        Support for analyzing trades and generate report. After analyzing trades, reset trades and initial capital.
        
        :param historical_data: DataFrame of historical data
        
        :return: None
        """
        profit_df = pd.DataFrame(self.profit_log)
        if profit_df.empty:
            self.notifier.send_message(f"🚨 {self.symbol}: No trades to analyze.")
            return

        capital = self.portfolio_manager.get_status(historical_data["close"].iloc[-1])["capital"]

        win_trades = profit_df[profit_df["profit"] > 0]
        loss_trades = profit_df[profit_df["profit"] <= 0]
        
        win_count = len(win_trades)
        loss_count = len(loss_trades)
        win_profit = win_trades["profit"].sum()
        loss_profit = loss_trades["profit"].sum()

        total_trades = len(profit_df)
        win_rate = win_count / total_trades if total_trades > 0 else 0
        profit_factor = abs(win_profit / loss_profit) if loss_profit < 0 else float("inf")
        earn_rate = (capital - self.portfolio_manager.initial_capital) / self.portfolio_manager.initial_capital
        origin_increase_rate = (historical_data["close"].iloc[-1] - historical_data["close"].iloc[0]) / historical_data["close"].iloc[0]

        avg_win = win_trades["profit"].mean() if win_count > 0 else 0
        avg_loss = loss_trades["profit"].mean() if loss_count > 0 else 0
        risk_reward_ratio = avg_win / abs(avg_loss) if avg_loss != 0 else float("inf")

        max_win = win_trades["profit"].max() if win_count > 0 else 0
        max_loss = loss_trades["profit"].min() if loss_count > 0 else 0

        report = (
            f"===== 🚀 {self.symbol} Strategy Report =====\n"
            f"Final Capital: {capital:.2f}\n"
            f"Earn Rate: {earn_rate:.2%}\n"
            f"Origin Increase Rate: {origin_increase_rate:.2%}\n"
            f"Win Trades: {win_count}\n"
            f"Lose Trades: {loss_count}\n"
            f"Win Rate: {win_rate:.2%}\n"
            f"Profit Factor: {profit_factor:.2f}\n"
            f"Risk-Reward Ratio: {risk_reward_ratio:.2f}\n"
            f"Max Win: {max_win:.2f}\n"
            f"Max Loss: {max_loss:.2f}\n"
        )
        
        self.notifier.send_message(report)

        self.trades = []
        self.portfolio_manager.initial_capital = self.portfolio_manager.capital

def sleep_until_next_hour():
    current_time = datetime.now()
    
    next_hour = current_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    
    sleep_duration = (next_hour - current_time).total_seconds()
    
    if sleep_duration > 0:
        time.sleep(sleep_duration)
    
    return next_hour 

if __name__ == '__main__':    
    load_dotenv()
    binance_api = BinanceAPI(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_SECRET_KEY'))
    notifier = TelegramNotifier(os.getenv('CHAT_TOKEN'), os.getenv('CHAT_ID'))
    
    symbol = "BTCUSDT"
    precision = binance_api.get_symbol_precision(symbol)
    portfolio_manager = PortfolioManager(100, 0.0005, 2, precision)
    agent = TradingAgent(binance_api, portfolio_manager, notifier, symbol)
    
    hours = 0
    while True:
        sleep_until_next_hour()
        hours += 1
        
        historical_data = agent.fetch_historical_data("1h", 24)
        macd, macd_signal, macd_hist = talib.MACD(historical_data["close"], fastperiod=12, slowperiod=26, signalperiod=9)
        
        if agent.portfolio_manager.position > 0:
            if macd_hist.iloc[-1] < 0:
                agent.close_position(historical_data["close"].iloc[-1])
        elif agent.portfolio_manager.position < 0:
            if macd_hist.iloc[-1] > 0:
                agent.close_position(historical_data["close"].iloc[-1])
                
        if hours % 24 == 0:
            agent.analyze(historical_data)
            hours = 0
        