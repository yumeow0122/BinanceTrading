import math

class PortfolioManager:
    def __init__(self, initial_capital=100, fee_rate=0.001, leverage=1, precision=3):
        """
        PortfolioManager for managing capital and position size
        
        param initial_capital: starting capital
        param fee_rate: trading fee rate
        param leverage: leverage rate
        param precision: number of decimal places for min position size
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.available_capital = initial_capital
        self.position = 0
        
        self.fee_rate = fee_rate
        self.leverage = leverage
        self.precision = precision

        self.__open_price = None
        
    def calculate_position(self, price, size=None):
        """
        Calculate position size based on current price
        
        param price: current price
        param size: specified buy size (optional), if not specified, use all capital to buy
        return: position size
        """
        max_position = self.available_capital * self.leverage / (price * (1 + self.fee_rate * self.leverage))
        
        if size is not None:
            position = min(size, max_position)
        else:
            position = max_position

        return self.truncate_to_precision(position)

    def update_balance(self, position=0, price=0, trade_type=""):
        """
        param position: position size, positive for long, negative for short
        param price: current price
        param trade_type: open or close
        return: None if open, gain if close
        """
        fee = abs(position) * price * self.fee_rate
        margin_cost = abs(position) * price / self.leverage

        if trade_type == "open":
            if self.position != 0:
                raise ValueError("Cannot open a new position before closing the existing one")

            total_cost = margin_cost + fee
            if total_cost > self.available_capital:
                raise ValueError("Not enough capital")
            
            self.position = position
            self.__open_price = price
            self.capital -= fee
            self.available_capital -= total_cost
            
        elif trade_type == "close":
            if self.position == 0:
                raise ValueError("No open position to close")

            gain = self.position * (price - self.__open_price)
            self.capital += gain - fee
            self.available_capital = self.capital
            self.position = 0 
            return gain
        else:
            raise ValueError("Invalid trade_type: must be 'open' or 'close'")

    def get_status(self, price):
        """
        param price: current price
        return: updated capital, position, available capital
        """
        gain = self.position * (price - self.__open_price) if self.position != 0 else 0

        return {
            "capital": self.capital + gain,
            "position": self.position,
            "available_capital": self.available_capital
        }

    def truncate_to_precision(self, value):
        factor = 10 ** self.precision
        return math.floor(value * factor) / factor

def test_calculate_position():
    capital = 100
    price = 100
    fee_rate = 0.001
    leverage = 2
    pm = PortfolioManager(capital, fee_rate, leverage, 3)
    
    expected_max_position = capital * leverage / (price * (1 + fee_rate * leverage))
    expected_max_position = pm.truncate_to_precision(expected_max_position)
    
    assert pm.calculate_position(100) == expected_max_position
    assert pm.calculate_position(100, 0.5) == 0.5
    assert pm.calculate_position(100, 1) == 1

def test_update_balance():
    pm = PortfolioManager(initial_capital=100, fee_rate=0.001, leverage=2, precision=3)

    position = pm.calculate_position(100)
    pm.update_balance(position=position, price=100, trade_type="open")
    assert pm.position == position
    assert pm.capital == 99.8004
    assert pm.available_capital == 0.00039999999999906777

    pm.update_balance(position=-position, price=110, trade_type="close")
    assert pm.position == 0
    assert pm.available_capital == 119.54084
    assert pm.capital == pm.available_capital

    position = pm.calculate_position(100)
    pm.update_balance(position=-position, price=100, trade_type="open")
    assert pm.position == -position
    assert pm.available_capital == 0.002239999999986253

    pm.update_balance(position=position, price=90, trade_type="close")
    assert pm.position == 0
    assert pm.available_capital == 142.9475
    assert pm.capital == pm.available_capital
  
if __name__ == "__main__":
    test_calculate_position()
    print("calculate_position passed")
    
    test_update_balance()
    print("update_balance passed")