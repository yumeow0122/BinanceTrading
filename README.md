# BinanceTrade

## Environment Installation
- Build Environment with **Docker**
    ```bash
    bash ./bash build.sh
    ```

- Setup with all environment variables in `.env`
    - `CHAT_ID` and `CHAT_TOKEN` are for Telegram API notifications.
    - **WARNING:** Do not set sensitive information in `.env.example`.

## BacktestAgent
### 📘 Introduction
- 🚀 **BacktestAgent** is a framework for backtesting algorithmic trading strategies.
- More sample at  `BacktestAgent.py`

### ⚙️ Features
| **Function**          | **Description** |
|------------------|--------------------------------|
| `open_position()`   | Opens a position; positive values for long, negative values for short |
| `close_position()` | Closes a position; positive values for long, negative values for short |
| `fetch_historical_data()`  | Retrieves historical market data based on symbol, interval, and day count |
| `get_status()` | Retrieves current trading status |
| `analyze()` | Analyzes the trading strategy performance |

## TradingAgent
### 📘 Introduction
- 🚀 **TradingAgent** is a framework for **Binance API** algorithmic trading with integrated Telegram notifications.
For supporting other exchanges or notifiers, extend the abstract base class (ABC) in `module/base`.

- More sample at  `TradingAgent.py`

### ⚙️ Features
| **Function**          | **Description** |
|------------------|--------------------------------|
| `open_long()`   | Opens a long position (buy) |
| `open_short()`  | Opens a short position (sell) |
| `close_position()` | Closes the current position |
| `fetch_historical_data()` | Retrieves Binance historical market data |
| `get_status()` | Retrieves current trading status |
| `analyze()` | Evaluates trading strategy performance |

## Usage
### ▶️ Running the Trading Bot
```bash
python trading_agent.py
```
This will start the trading bot, monitoring the market and executing trades based on strategy conditions.

### 🔑 Configuration
Ensure the following variables are set in `.env`:
```env
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
CHAT_TOKEN=your_telegram_token
CHAT_ID=your_telegram_chat_id
```

### 📡 Notifications
- All trade actions (open/close positions) and errors are sent to Telegram.
- Modify `Notifier` in `module/notifier` to customize messaging.

### 🚀 ExchangeAPI
- **ExchangeAPI** is an abstraction layer for integrating different cryptocurrency exchanges.
- Modify `ExchangeAPI` in `module/ExchangeAPI` to customize messaging.

#### ⚙️ Features
| **Function**          | **Description** |
|------------------|--------------------------------|
| `place_market_order()` | Executes a market order (buy/sell) on the exchange |
| `fetch_historical_data()` | Retrieves historical market data from the exchange |
| `get_symbol_precision()` | Gets the decimal precision for a given trading pair |
| `check_account_balance()` | Fetches account balance details |