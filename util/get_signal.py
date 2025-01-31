import pandas as pd
import talib

def calculate_macd_signal(row, prev_hist):
    if prev_hist is not None:
        if prev_hist < 0 and row["MACD_hist"] > 0:
            return 1
        elif prev_hist > 0 and row["MACD_hist"] < 0:
            return -1
    return 0

def calculate_rsi_signal(row, prev_rsi):
    if prev_rsi is not None:
        if prev_rsi > 70 and row["RSI"] <= 70:
            return -1
        elif prev_rsi < 30 and row["RSI"] >= 30:
            return 1
    return 0

def calculate_kd_signal(row, prev_k, prev_d):
    if prev_k is not None and prev_d is not None:
        if prev_k < prev_d and row["%K"] > row["%D"]:
            return 1
        elif prev_k > prev_d and row["%K"] < row["%D"]:
            return -1
    return 0

def calculate_aroon_signal(row):
    if row["Aroon_Up"] > 50 and row["Aroon_Up"] >= 100 and row["Aroon_Down"] < 50:
        return 1
    elif row["Aroon_Down"] > 50 and row["Aroon_Down"] >= 100 and row["Aroon_Up"] < 50:
        return -1
    return 0 
    
def calculate_trade_signals(file_path: str, output_path: str) -> pd.DataFrame:
    """
    計算技術指標並生成交易信號，將結果儲存到 CSV 文件中。
    
    :param file_path: 輸入 CSV 文件的路徑
    :param output_path: 輸出 CSV 文件的路徑
    :return: 包含交易信號的 DataFrame
    """
    with open(file_path) as f:
        df = pd.read_csv(f)
    df["Open"] = df["Open"].astype(float)
    df["High"] = df["High"].astype(float)
    df["Low"] = df["Low"].astype(float)
    df["Close"] = df["Close"].astype(float)
    df["Volume"] = df["Volume"].astype(float)

    df["SMA_20"] = talib.SMA(df["Close"], timeperiod=20)
    df["EMA_20"] = talib.EMA(df["Close"], timeperiod=20)
    df["RSI"] = talib.RSI(df["Close"], timeperiod=14)
    df["MACD"], df["MACD_signal"], df["MACD_hist"] = talib.MACD(df["Close"], fastperiod=12, slowperiod=26, signalperiod=9)
    df["%K"], df["%D"] = talib.STOCH(df["High"], df["Low"], df["Close"], fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
    df["CCI"] = talib.CCI(df["High"], df["Low"], df["Close"], timeperiod=14)

    df["Momentum"] = talib.MOM(df["Close"], timeperiod=10)
    df["WILLR"] = talib.WILLR(df["High"], df["Low"], df["Close"], timeperiod=14)
    df["TRIX"] = talib.TRIX(df["Close"], timeperiod=15)
    df["Aroon_Up"], df["Aroon_Down"] = talib.AROON(df["High"], df["Low"], timeperiod=14)

    def indicator_signals(row, prev_macd_hist, prev_rsi, prev_k, prev_d):
        sma_sig = 1 if row["Close"] > 1.005 * row["SMA_20"] else (-1 if row["Close"] < 0.995 * row["SMA_20"] else 0)
        rsi_sig = calculate_rsi_signal(row, prev_rsi)
        macd_sig = calculate_macd_signal(row, prev_macd_hist)
        kd_sig = calculate_kd_signal(row, prev_k, prev_d)
        cci_sig = 1 if row["CCI"] > 100 else (-1 if row["CCI"] < -100 else 0)
        
        momentum_sig = 1 if row["Momentum"] > 0 else -1
        willr_sig = 1 if row["WILLR"] < -80 else (-1 if row["WILLR"] > -20 else 0)
        trix_sig = 1 if row["TRIX"] > 0 else -1
        aroon_sig = calculate_aroon_signal(row)

        total_signal = (
            0.1 * sma_sig +
            0.1 * rsi_sig +
            0.1 * macd_sig +
            0.1 * kd_sig +
            0.1 * cci_sig +
            0.1 * momentum_sig +
            0.05 * willr_sig +
            0.05 * trix_sig +
            0.05 * aroon_sig
        )
        return round(total_signal, 2)

    macd_signals = []
    rsi_signals = []
    prev_macd_hist = None
    prev_rsi = None
    prev_k = None
    prev_d = None
    for _, row in df.iterrows():
        macd_signal = calculate_macd_signal(row, prev_macd_hist)
        rsi_signal = calculate_rsi_signal(row, prev_rsi)
        macd_signals.append(macd_signal)
        rsi_signals.append(rsi_signal)
        prev_macd_hist = row["MACD_hist"]
        prev_rsi = row["RSI"]
        prev_k = row["%K"]
        prev_d = row["%D"]

    df["Trade_Signal"] = df.apply(
        lambda row: indicator_signals(row, prev_macd_hist, prev_rsi, prev_k, prev_d), axis=1
    )

    df = df[["Open", "High", "Low", "Close", "Volume", "Trade_Signal"]]

    df.to_csv(output_path, index=False)

    return df

def main():
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    for symbol in symbols:
        file_path = f"./data/{symbol}_4h_klines.csv"
        output_path = f"./data/{symbol}_4h_signals.csv"
        calculate_trade_signals(file_path, output_path)
    
if __name__ == "__main__":
    main()