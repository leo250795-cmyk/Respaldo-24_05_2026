import pandas as pd

try:
    df = pd.read_csv("analytics/trade_outcomes.csv")

except Exception as e:
    print(f"Error loading trade outcomes: {e}")
    exit()

if len(df) == 0:
    print("No trade outcomes.")
    exit()

print("\n🧠 AI LEARNING ENGINE\n")

if "AI Conviction" in df.columns:

    conviction_stats = (
        df.groupby("AI Conviction")["PnL %"]
        .mean()
        .sort_values(ascending=False)
    )

    print("🔥 Conviction Learning:\n")
    print(conviction_stats)

if "Opportunity Type" in df.columns:

    opportunity_stats = (
        df.groupby("Opportunity Type")["PnL %"]
        .mean()
        .sort_values(ascending=False)
    )

    print("\n🚀 Opportunity Learning:\n")
    print(opportunity_stats)

if "Market Sentiment" in df.columns:

    sentiment_stats = (
        df.groupby("Market Sentiment")["PnL %"]
        .mean()
        .sort_values(ascending=False)
    )

    print("\n🌎 Sentiment Learning:\n")
    print(sentiment_stats)

best_conviction = None
best_opportunity = None

if "AI Conviction" in df.columns:

    best_conviction = (
        df.groupby("AI Conviction")["PnL %"]
        .mean()
        .idxmax()
    )

if "Opportunity Type" in df.columns:

    best_opportunity = (
        df.groupby("Opportunity Type")["PnL %"]
        .mean()
        .idxmax()
    )

print("\n🏆 AI BEST LEARNINGS\n")

print(f"Best Conviction: {best_conviction}")
print(f"Best Opportunity: {best_opportunity}")