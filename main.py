# main.py

from fastapi import FastAPI, HTTPException
from src.strategies import ScalpingStrategy, MomentumStrategy, ArbitrageStrategy, TrendFollowingStrategy, MeanReversionStrategy
from src.data.data_handler import DataHandler
from src.execution.broker_interface import BrokerInterface
from src.monitoring.monitor import Monitor
from src.utils.logger import setup_logger
from src.utils.security import Security
from src.models.training import ModelTrainer
from src.backtesting.backtester import Backtester, TestStrategy
from dotenv import load_dotenv
import os
import backtrader as bt

load_dotenv()

app = FastAPI()

# Setup Logger
setup_logger()

# Initialize Security
security = Security()

# Initialize Data Handler with API Keys
api_keys = {
    "alpha_vantage": os.getenv("ALPHA_VANTAGE_API_KEY"),
    "iex_cloud": os.getenv("IEX_CLOUD_API_KEY"),
    "binance": os.getenv("BINANCE_API_KEY"),
    "interactive_brokers": os.getenv("INTERACTIVE_BROKERS_API_KEY"),
    "alpaca": os.getenv("ALPACA_API_KEY"),
    "coinbasepro": os.getenv("COINBASEPRO_API_KEY"),
    # Add other API keys
}
data_handler = DataHandler(api_keys=api_keys)

# Initialize Broker Interface with Broker API Keys
broker_api_keys = {
    "interactivebrokers": os.getenv("INTERACTIVEBROKERS_API_KEY"),
    "alpaca": os.getenv("ALPACA_API_KEY"),
    "binance": os.getenv("BINANCE_API_KEY"),
    "coinbasepro": os.getenv("COINBASEPRO_API_KEY"),
    # Add other broker API keys
}
broker_interface = BrokerInterface(broker_api_keys=broker_api_keys)

# Initialize Monitor with Email Configuration
email_config = {
    "from_email": os.getenv("FROM_EMAIL"),
    "to_email": os.getenv("TO_EMAIL"),
    "smtp_server": os.getenv("SMTP_SERVER"),
    "smtp_port": os.getenv("SMTP_PORT"),
    "password": os.getenv("EMAIL_PASSWORD"),
}
monitor = Monitor(email_config=email_config)

# Initialize Strategies
scalping = ScalpingStrategy()
momentum = MomentumStrategy()
arbitrage = ArbitrageStrategy()
trend_following = TrendFollowingStrategy()
mean_reversion = MeanReversionStrategy()

# Initialize Model Trainer
model_trainer = None  # Will be initialized when training starts

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/trade")
def trade(symbol: str):
    try:
        # Fetch Data
        data = data_handler.fetch_data(symbol=symbol, market="cryptocurrency", timeframe="1m")  # Example for crypto
        
        if data.empty:
            raise ValueError("No data fetched for the given symbol and market.")
        
        # Execute Strategies
        result_scalping = scalping.execute_trade(symbol)
        result_momentum = momentum.execute_trade(symbol)
        result_arbitrage = arbitrage.execute_trade(symbol)
        result_trend = trend_following.execute_trade(symbol)
        result_mean_reversion = mean_reversion.execute_trade(symbol)
        
        # Compile Results
        trade_results = {
            "scalping": result_scalping,
            "momentum": result_momentum,
            "arbitrage": result_arbitrage,
            "trend_following": result_trend,
            "mean_reversion": result_mean_reversion
        }
        
        # Execute Trades on Multiple Brokerages
        for broker in broker_api_keys.keys():
            success = broker_interface.execute_order(
                broker=broker,
                symbol=symbol,
                action="buy",
                quantity=10  # Example quantity; adjust as needed
            )
            if not success:
                monitor.send_email_alert(subject="QuantumTrader Execution Error", message=f"Failed to execute order on {broker} for {symbol}.")
        
        # Log Event
        monitor.log_event(f"Executed trades for {symbol}")
        
        return {"trade_results": trade_results}
    except Exception as e:
        monitor.send_email_alert(subject="QuantumTrader Error", message=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train")
def train_model(symbol: str):
    global model_trainer
    try:
        # Fetch Data
        data = data_handler.fetch_data(symbol=symbol, market="cryptocurrency", timeframe="1m")  # Example for crypto
        
        if data.empty:
            raise ValueError("No data fetched for the given symbol and market.")
        
        # Initialize Model Trainer
        model_trainer = ModelTrainer(data=data)
        
        # Prepare Data
        X_train, X_test, y_train, y_test = model_trainer.prepare_data()
        
        # Train Models
        model_trainer.train_random_forest(X_train, y_train, X_test, y_test)
        model_trainer.train_neural_network(X_train, y_train, X_test, y_test)
        
        # Save Model
        model_trainer.save_model(f"models/{symbol}_model.h5")
        
        return {"status": "Model trained and saved successfully."}
    except Exception as e:
        monitor.send_email_alert(subject="QuantumTrader Training Error", message=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/backtest")
def backtest(symbol: str):
    try:
        # Fetch Historical Data
        data = data_handler.fetch_data(symbol=symbol, market="cryptocurrency", timeframe="1m")  # Example for crypto
        
        if data.empty:
            raise ValueError("No data fetched for the given symbol and market.")
        
        # Prepare Data for Backtrader
        data_bt = bt.feeds.PandasData(dataname=data)
        
        # Initialize Backtester
        backtester = Backtester(data=data_bt, strategy=TestStrategy)
        
        # Run Backtest
        backtester.run_backtest()
        
        return {"status": "Backtest completed successfully."}
    except Exception as e:
        monitor.send_email_alert(subject="QuantumTrader Backtest Error", message=str(e))
        raise HTTPException(status_code=500, detail=str(e))
