# src/backtesting/backtester.py

import backtrader as bt
from loguru import logger
import os

class TestStrategy(bt.Strategy):
    def __init__(self):
        self.dataclose = self.datas[0].close
    
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        logger.info(f"{dt.isoformat()} {txt}")
    
    def next(self):
        self.log(f"Close: {self.dataclose[0]}")
        if not self.position:
            if self.dataclose[0] < self.dataclose[-1]:
                if self.dataclose[-1] < self.dataclose[-2]:
                    self.log("BUY CREATE")
                    self.buy()
        else:
            if len(self) >= (self.bar_executed + 5):
                self.log("SELL CREATE")
                self.sell()

class Backtester:
    def __init__(self, data: bt.feeds.PandasData, strategy=TestStrategy):
        self.data = data
        self.strategy = strategy
        self.cerebro = bt.Cerebro()
        self.cerebro.addstrategy(self.strategy)
        self.cerebro.adddata(self.data)
        self.cerebro.broker.setcash(10000.0)
        self.cerebro.broker.setcommission(commission=0.001)
    
    def run_backtest(self):
        logger.info('Starting Backtest')
        self.cerebro.run()
        logger.info('Backtest Completed')
        self.cerebro.plot()
