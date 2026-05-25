import yfinance as yf
import pandas as pd
import ta

tickers = ["NVDA", "SMCI", "AMD", "ACHR", "PLTR"]

data = []

print("\n=== J-AI SCANNER V2 ===\n")

for ticker in tickers:

    stock = yf.Ticker(ticker)
    hist = stock.history(period="1mo")

    if len(hist) < 20:
        continue

    current_price = hist["Close"].iloc[-1]
    previous_price = hist["Close"].iloc[-2]

    change_percent = ((current_price - previous_price) / previous_price) * 100

    avg_volume = hist["Volume"].tail(20).mean()
    current_volume = hist["Volume"].iloc[-1]

    relative_volume = current_volume / avg_volume

    rsi = ta.momentum.RSIIndicator(hist["Close"]).rsi().iloc[-1]

    # SCORE J-AI
    score = 0

    # RVOL
    if relative_volume > 3:
        score += 30
    elif relative_volume > 2:
        score += 20
    elif relative_volume > 1:
        score += 10

    # Momentum
    if change_percent > 5:
        score += 25
    elif change_percent > 2:
        score += 15
    elif change_percent > 0:
        score += 5

    # RSI
    if 60 <= rsi <= 80:
        score += 20

    # Price Trend
    if current_price > hist["Close"].rolling(20).mean().iloc[-1]:
        score += 15

    # Continuation
    if hist["Close"].iloc[-1] > hist["Close"].iloc[-5]:
        score += 10

    data.append({
        "Ticker": ticker,
        "Price": round(current_price, 2),
        "% Change": round(change_percent, 2),
        "RVOL": round(relative_volume, 2),
        "RSI": round(rsi, 2),
        "J-AI Score": score
    })

df = pd.DataFrame(data)

df = df.sort_values(by="J-AI Score", ascending=False)

print(df)

print("\n=== TOP MOMENTUM ===\n")

top = df.iloc[0]

print(f"""
Ticker: {top['Ticker']}
Score: {top['J-AI Score']}
RVOL: {top['RVOL']}
RSI: {top['RSI']}
""")