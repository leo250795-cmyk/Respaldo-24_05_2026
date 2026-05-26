import pandas as pd

try:
    df = pd.read_csv("logs/background_scanner.csv")

except Exception as e:
    print(f"Error loading scanner data: {e}")
    exit()

if len(df) == 0:
    print("No scanner data.")
    exit()

#print("Columnas disponibles:")
#print(df.columns.tolist())

results = []

for _, row in df.iterrows():

    try:

        entry = row["Entry Price"]

        target = row["Target 1"]

        current = row["Price"]

        pnl_percent = (
            (current - entry) / entry
        ) * 100

        result = "Neutral"

        if current >= target:
            result = "Winner"

        elif pnl_percent <= -3:
            result = "Loser"

        results.append({
            "Ticker": row["Ticker"],
            "Entry": entry,
            "Current": current,
            "PnL %": round(pnl_percent, 2),
            "Result": result,
            "AI Conviction": row.get("AI Conviction", "None"),
            "Opportunity Type": row.get("Opportunity Type", "None"),
            "Market Sentiment": row.get("Market Sentiment", "None"),
        })

    except Exception as e:
        print(f"Error processing row: {e}")

results_df = pd.DataFrame(results)

results_df.to_csv(
    "analytics/trade_outcomes.csv",
    index=False
)

print("✅ Trade outcomes updated.")