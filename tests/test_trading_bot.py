# tests/test_trading_bot.py

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_trade_endpoint():
    response = client.post("/trade", json={"symbol": "AAPL"})
    assert response.status_code == 200
    assert "trade_results" in response.json()
    assert "scalping" in response.json()["trade_results"]
    assert "momentum" in response.json()["trade_results"]
    assert "arbitrage" in response.json()["trade_results"]
    assert "trend_following" in response.json()["trade_results"]
    assert "mean_reversion" in response.json()["trade_results"]

def test_train_endpoint():
    response = client.post("/train", json={"symbol": "AAPL"})
    assert response.status_code == 200
    assert response.json()["status"] == "Model trained and saved successfully."

def test_backtest_endpoint():
    response = client.post("/backtest", json={"symbol": "AAPL"})
    assert response.status_code == 200
    assert response.json()["status"] == "Backtest completed successfully."
