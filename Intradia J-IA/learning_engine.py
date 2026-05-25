import pandas as pd
import yfinance as yf

LEARNING_FILE = "logs/j_ai_learning_dataset.csv"

df = pd.read_csv(LEARNING_FILE, on_bad_lines="skip")

if df.empty:
    print("No hay señales para validar.")
    exit()

updated_rows = []

for _, row in df.iterrows():
    ticker = row["Ticker"]

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d", interval="5m", prepost=True)

        if hist.empty:
            updated_rows.append(row)
            continue

        future_price = hist["Close"].iloc[-1]
        entry = row["Entry"]
        stop = row["Stop"]
        target = row["Target"]

        future_return = ((future_price - entry) / entry) * 100

        row["Future Price"] = round(future_price, 2)
        row["Future Return %"] = round(future_return, 2)
        row["Hit Target"] = future_price >= target
        row["Hit Stop"] = future_price <= stop
        row["Reached +5%"] = future_return >= 5

        if future_price >= target or future_return >= 5:
            row["Learning Result"] = "Winner"
        elif future_price <= stop:
            row["Learning Result"] = "Loser"
        else:
            row["Learning Result"] = "Open"

        updated_rows.append(row)

    except Exception as e:
        print(f"Error con {ticker}: {e}")
        updated_rows.append(row)

updated_df = pd.DataFrame(updated_rows)

updated_df.to_csv(
    LEARNING_FILE,
    index=False
)

print("✅ Learning dataset actualizado.")