# app.py

import streamlit as st
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

st.title("QuantumTrader Dashboard")

st.header("Trade Execution")
symbol = st.text_input("Enter Symbol (e.g., AAPL):")
if st.button("Execute Trade"):
    if symbol:
        response = requests.post("http://localhost:8888/trade", json={"symbol": symbol})
        if response.status_code == 200:
            st.success("Trade Executed Successfully!")
            st.json(response.json())
        else:
            st.error(f"Trade Execution Failed: {response.json().get('detail')}")
    else:
        st.warning("Please enter a valid symbol.")

st.header("Train Model")
if st.button("Train Model for Symbol"):
    if symbol:
        response = requests.post("http://localhost:8888/train", json={"symbol": symbol})
        if response.status_code == 200:
            st.success("Model Trained Successfully!")
            st.json(response.json())
        else:
            st.error(f"Model Training Failed: {response.json().get('detail')}")
    else:
        st.warning("Please enter a valid symbol.")

st.header("Backtesting")
symbol_bt = st.text_input("Enter Symbol for Backtest (e.g., AAPL):")
if st.button("Run Backtest"):
    if symbol_bt:
        response = requests.post("http://localhost:8888/backtest", json={"symbol": symbol_bt})
        if response.status_code == 200:
            st.success("Backtest Completed Successfully!")
            st.json(response.json())
        else:
            st.error(f"Backtest Failed: {response.json().get('detail')}")
    else:
        st.warning("Please enter a valid symbol.")

st.header("Chat with QuantumTrader")
user_input = st.text_input("You:", "")
if st.button("Send"):
    if user_input:
        chat_response = get_chatgpt_response(user_input)
        st.text_area("QuantumTrader:", value=chat_response, height=200)
    else:
        st.warning("Please enter a message to send.")

def get_chatgpt_response(message):
    api_key = os.getenv("CHATGPT_API_KEY")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": message}]
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Error: Unable to fetch response from ChatGPT."
