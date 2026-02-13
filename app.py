import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.title("📈 Stock Analyzer – Investment Score")

ticker = st.text_input("Enter Ticker (e.g., AAPL, MSFT, TSLA):")

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

def technical_block(price_history):
    if len(price_history) < 200:
        return 0

    close = price_history
    last_price = close.iloc[-1]

    ma20 = close.rolling(20).mean().iloc[-1]
    ma50 = close.rolling(50).mean().iloc[-1]
    ma200 = close.rolling(200).mean().iloc[-1]

    if last_price > ma20 and last_price > ma50 and last_price > ma200:
        trend = 6
    elif last_price > ma50 and last_price > ma200:
        trend = 4
    elif last_price > ma200:
        trend = 2
    else:
        trend = 0

    rsi = calc_rsi(close).iloc[-1]
    macd_line = ema(close, 12) - ema(close, 26)
    signal_line = ema(macd_line, 9)

    if 50 <= rsi <= 65 and macd_line.iloc[-1] > signal_line.iloc[-1]:
        momentum = 6
    elif 40 <= rsi < 50:
        momentum = 3
    else:
        momentum = 0

    high_3m = close.iloc[-63:].max()
    if last_price >= high_3m:
        breakout = 4
    elif last_price > ma50:
        breakout = 2
    else:
        breakout = 0

    if 50 <= rsi <= 70:
        sentiment = 4
    elif 40 <= rsi < 50:
        sentiment = 3
    elif 30 <= rsi < 40:
        sentiment = 1
    else:
        sentiment = 0

    return trend + momentum + breakout + sentiment

def growth_block(info):
    score = 0
    rev_growth = info.get("revenueGrowth")
    eps_growth = info.get("earningsQuarterlyGrowth")

    if rev_growth:
        if rev_growth > 0.2:
            score += 15
        elif rev_growth > 0.1:
            score += 10
        elif rev_growth > 0.03:
            score += 5

    if eps_growth:
        if eps_growth > 0.2:
            score += 15
        elif eps_growth > 0.1:
            score += 10
        elif eps_growth > 0.05:
            score += 5

    return min(score, 40)

def valuation_block(info, price):
    score = 0
    pe = info.get("forwardPE")
    peg = info.get("pegRatio")
    target = info.get("targetMeanPrice")

    if pe:
        if pe < 15:
            score += 10
        elif pe < 20:
            score += 7
        elif pe < 30:
            score += 3

    if peg and peg > 0:
        if peg < 1.2:
            score += 10
        elif peg < 1.8:
            score += 7
        elif peg < 2.5:
            score += 3

    if target and price:
        upside = (target - price) / price
        if upside > 0.25:
            score += 10
        elif upside > 0.1:
            score += 7
        elif upside > 0:
            score += 3

    return min(score, 35)

def quality_block(info):
    score = 0
    roe = info.get("returnOnEquity")
    debt = info.get("debtToEquity")

    if roe:
        if roe > 0.18:
            score += 10
        elif roe > 0.1:
            score += 7
        elif roe > 0.05:
            score += 3

    if debt:
        if debt < 0.3:
            score += 10
        elif debt < 0.7:
            score += 7
        elif debt < 1.2:
            score += 3

    return min(score, 25)

if ticker:
    stock = yf.Ticker(ticker)
    info = stock.info
    hist = stock.history(period="1y")["Close"]

    if hist.empty:
        st.error("No data found for this ticker.")
    else:
        price = hist.iloc[-1]

        g = growth_block(info)
        v = valuation_block(info, price)
        q = quality_block(info)
        t = technical_block(hist)

        final = round((g + v + q + t) / 120 * 100, 2)

        st.subheader("Results")
        st.write(f"**Growth:** {g}/40")
        st.write(f"**Valuation:** {v}/35")
        st.write(f"**Quality:** {q}/25")
        st.write(f"**Technical:** {t}/20")
        st.write(f"### Final Score: **{final}/100**")


