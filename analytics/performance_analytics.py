import pandas as pd

try:
    df = pd.read_csv("analytics/trade_outcomes.csv")

except Exception as e:
    print(f"Error loading outcomes: {e}")
    exit()

if len(df) == 0:
    print("No trade outcomes.")
    exit()

total_trades = len(df)

winners = len(df[df["Result"] == "Winner"])

losers = len(df[df["Result"] == "Loser"])

winrate = (
    winners / total_trades
) * 100 if total_trades > 0 else 0

average_pnl = df["PnL %"].mean()

print("\n📊 PERFORMANCE ANALYTICS\n")

print(f"Total Trades: {total_trades}")
print(f"Winners: {winners}")
print(f"Losers: {losers}")

print(f"\n🏆 Winrate: {winrate:.2f}%")

print(f"📈 Average PnL: {average_pnl:.2f}%")

if "Opportunity Type" in df.columns:

    print("\n🔥 Opportunity Type Performance:\n")

    opportunity_stats = (
        df.groupby("Opportunity Type")["PnL %"]
        .mean()
        .sort_values(ascending=False)
    )

    print(opportunity_stats)

if "AI Conviction" in df.columns:

    print("\n🧠 Conviction Performance:\n")

    conviction_stats = (
        df.groupby("AI Conviction")["PnL %"]
        .mean()
        .sort_values(ascending=False)
    )

    print(conviction_stats)