import os
from dotenv import load_dotenv

from module.BinanceAPI import BinanceAPI
from module.PortfolioManager import PortfolioManager

class BacktestAgent:
    def __init__(self, binance_api, portfolio_manager):
        self.binance_api = binance_api
        self.portfolio_manager = portfolio_manager
        self.trade_log = []
        self.profit_log = []
        
    def fetch_historical_data(self, symbol, interval, days):
        """
        Fetch historical data from Binance API
        
        param symbol: trading pair
        param interval: time interval
        param days: number of days
        """
        return self.binance_api.fetch_historical_data(symbol, interval, days)

    def open_position(self, side, price, size=None):
        """
        Simulate opening a position
        
        param side: BUY or SELL
        param price: current price
        param size: specified buy size (optional), if not specified, use all capital to buy
        """
        position = size if size else self.portfolio_manager.calculate_position(price)
        if side == "BUY":
            self.portfolio_manager.update_balance(position, price, "open")
            
        elif side == "SELL":
            self.portfolio_manager.update_balance(-position, price, "open")
            
        self.trade_log.append({"type": "open", "side": side, "price": price, "size": position})
    
    def close_position(self, price):
        """
        Simulate closing a position
        
        param price: current price
        """
        position = self.portfolio_manager.position
        gain = self.portfolio_manager.update_balance(position, price, "close")
        side = "SELL" if position > 0 else "BUY"
        
        self.trade_log.append({"type": "close", "side": side, "price": price, "size": abs(position)})
        self.profit_log.append({"side": "LONG" if position > 0 else "SHORT", "profit": gain})
        
    def get_status(self, price):
        """
        Get current status of the portfolio
        
        param price: current price
        
        return: status of the portfolio
        """
        return self.portfolio_manager.get_status(price)
    
    def analyze(self, symbol, historical_data):
        """
        Analyze the backtest results
        
        param symbol: trading pair
        param historical_data: historical data of the trading
        """
        if self.portfolio_manager.position != 0:
            self.close_position(historical_data["close"].iloc[-1])
        
        win_count = 0
        loss_count = 0
        win_profit = 0
        loss_profit = 0

        for log in self.profit_log:
            profit = log["profit"]
            if profit > 0:
                win_count += 1
                win_profit += profit

            else:
                loss_count += 1
                loss_profit += profit

        total_trades = len(self.profit_log)
        win_rate = win_count / total_trades if total_trades > 0 else 0
        profit_factor = abs(win_profit / loss_profit) if loss_profit < 0 else float("inf")
        earn_rate = (self.portfolio_manager.capital - self.portfolio_manager.initial_capital) / self.portfolio_manager.initial_capital
        origin_increase_rate = (historical_data["close"].iloc[-1] - historical_data["close"].iloc[0]) / historical_data["close"].iloc[0]

        print(f"=== {symbol} Strategy Report ===")
        print(f"Final Capital: {self.portfolio_manager.capital:.2f}")
        print(f"Earn Rate: {earn_rate:.2%}")
        print(f"Origin Increase Rate: {origin_increase_rate:.2%}")
        print(f"Win Trades: {win_count}")
        print(f"Lose Trades: {loss_count}")
        print(f"Win Rate: {win_rate:.2%}")
        print(f"Profit Factor: {profit_factor:.2f}")

if __name__ == '__main__':
    import os
    import talib
    import pandas as pd
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    # Initialize Binance API
    symbol = 'BTCUSDT'
    binance_api = BinanceAPI(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_SECRET_KEY'))

    # Setup Portfolio Manager
    precision = binance_api.get_symbol_precision(symbol)
    pm = PortfolioManager(initial_capital=100, fee_rate=0.0005, leverage=2, precision=3)
    backtest_agent = BacktestAgent(binance_api, pm)

    # Fetch historical data
    df = binance_api.fetch_historical_data(symbol, '1h', 30)  # Fetch last 30 days of data

    # Calculate MACD
    df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)

    # Strategy Execution
    for i in range(1, len(df)):
        price = df['close'].iloc[i]
        if backtest_agent.portfolio_manager.position == 0 and df['macd'].iloc[i] > df['macd_signal'].iloc[i] and df['macd'].iloc[i - 1] <= df['macd_signal'].iloc[i - 1]:
            backtest_agent.open_position("BUY", price)
        elif backtest_agent.portfolio_manager.position > 0 and df['macd'].iloc[i] < df['macd_signal'].iloc[i] and df['macd'].iloc[i - 1] >= df['macd_signal'].iloc[i - 1]:
            backtest_agent.close_position(price)

    # Analyze results
    backtest_agent.analyze(symbol, df)