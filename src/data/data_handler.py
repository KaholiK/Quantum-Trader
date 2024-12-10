# src/data/data_handler.py

import requests
import pandas as pd
from ta import trend, momentum, volatility, volume
from loguru import logger

class DataHandler:
    def __init__(self, api_keys: dict):
        self.api_keys = api_keys
    
    def fetch_data(self, symbol: str, market: str, timeframe: str):
        # Implement data fetching from multiple APIs based on market
        if market.lower() == "cryptocurrency":
            return self.fetch_binance_data(symbol, timeframe)
        elif market.lower() == "stocks":
            return self.fetch_alpha_vantage_data(symbol, timeframe)
        elif market.lower() == "forex":
            return self.fetch_iex_cloud_data(symbol, timeframe)
        elif market.lower() == "commodities":
            return self.fetch_alpha_vantage_data(symbol, timeframe)
        else:
            logger.error(f"Market {market} not supported yet.")
            return pd.DataFrame()
    
    def fetch_binance_data(self, symbol: str, timeframe: str):
        try:
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol.upper()}&interval={timeframe}"
            response = requests.get(url)
            data = response.json()
            df = pd.DataFrame(data, columns=['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 
                                             'Close Time', 'Quote Asset Volume', 'Number of Trades', 
                                             'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore'])
            # Convert to appropriate data types
            df['Close'] = pd.to_numeric(df['Close'])
            df['Volume'] = pd.to_numeric(df['Volume'])
            # Add technical indicators
            df = self.add_indicators(df)
            return df
        except Exception as e:
            logger.error(f"Error fetching Binance data: {e}")
            return pd.DataFrame()
    
    def fetch_alpha_vantage_data(self, symbol: str, timeframe: str):
        try:
            api_key = self.api_keys.get("alpha_vantage")
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={timeframe}&apikey={api_key}&outputsize=full&datatype=json"
            response = requests.get(url)
            data = response.json()
            time_series_key = f"Time Series ({timeframe})"
            if time_series_key not in data:
                logger.error(f"Alpha Vantage data not available for {symbol} with interval {timeframe}")
                return pd.DataFrame()
            df = pd.DataFrame.from_dict(data[time_series_key], orient='index')
            df = df.rename(columns={
                '1. open': 'Open',
                '2. high': 'High',
                '3. low': 'Low',
                '4. close': 'Close',
                '5. volume': 'Volume'
            })
            df.index = pd.to_datetime(df.index)
            df = df.astype(float)
            # Add technical indicators
            df = self.add_indicators(df)
            return df
        except Exception as e:
            logger.error(f"Error fetching Alpha Vantage data: {e}")
            return pd.DataFrame()
    
    def fetch_iex_cloud_data(self, symbol: str, timeframe: str):
        try:
            api_key = self.api_keys.get("iex_cloud")
            url = f"https://cloud.iexapis.com/stable/stock/{symbol}/chart/{timeframe}?token={api_key}"
            response = requests.get(url)
            data = response.json()
            df = pd.DataFrame(data)
            df['close'] = pd.to_numeric(df['close'])
            df['volume'] = pd.to_numeric(df['volume'])
            # Add technical indicators
            df = self.add_indicators(df)
            return df
        except Exception as e:
            logger.error(f"Error fetching IEX Cloud data: {e}")
            return pd.DataFrame()
    
    def add_indicators(self, df: pd.DataFrame):
        # Add various technical indicators
        try:
            # Trend Indicators
            df['SMA'] = trend.sma_indicator(df['Close'], window=20)
            df['EMA'] = trend.ema_indicator(df['Close'], window=20)
            df['MACD'] = trend.macd(df['Close'])
            df['MACD_signal'] = trend.macd_signal(df['Close'])
            df['MACD_diff'] = trend.macd_diff(df['Close'])
            
            # Momentum Indicators
            df['RSI'] = momentum.rsi(df['Close'], window=14)
            df['Stochastic'] = momentum.stoch(df['High'], df['Low'], df['Close'], window=14)
            
            # Volatility Indicators
            df['Bollinger_High'] = volatility.bollinger_hband(df['Close'], window=20, window_dev=2)
            df['Bollinger_Low'] = volatility.bollinger_lband(df['Close'], window=20, window_dev=2)
            
            # Volume Indicators
            df['Volume_Average'] = volume.volume_weighted_average_price(df['Close'], df['Volume'])
            
            return df
        except Exception as e:
            logger.error(f"Error adding indicators: {e}")
            return df
