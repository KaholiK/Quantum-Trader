# src/models/training.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from loguru import logger
import os

class ModelTrainer:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.model = None
    
    def prepare_data(self):
        # Feature Engineering
        X = self.data[['SMA', 'EMA', 'MACD', 'RSI', 'Bollinger_High', 'Bollinger_Low', 'Volume_Average']]
        y = (self.data['Close'].shift(-1) > self.data['Close']).astype(int)  # Binary classification
        
        # Drop last row with NaN
        X = X[:-1]
        y = y[:-1]
        
        # Split Data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        return X_train, X_test, y_train, y_test
    
    def train_random_forest(self, X_train, y_train, X_test, y_test):
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        predictions = rf.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        logger.info(f"Random Forest Accuracy: {accuracy}")
        self.model = rf
    
    def train_neural_network(self, X_train, y_train, X_test, y_test):
        model = Sequential()
        model.add(Dense(64, input_dim=X_train.shape[1], activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(1, activation='sigmoid'))
        
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        model.fit(X_train, y_train, epochs=50, batch_size=32, verbose=0)
        
        loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
        logger.info(f"Neural Network Accuracy: {accuracy}")
        self.model = model
    
    def save_model(self, path: str):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.model.save(path)
            logger.info(f"Model saved at {path}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
