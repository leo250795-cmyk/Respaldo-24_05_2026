import json
import pandas as pd

OUTCOMES_FILE = "analytics/trade_outcomes.csv"
OPTIMIZED_WEIGHTS_FILE = "config/optimized_ai_weights.json"

df = pd.read_csv(OUTCOMES_FILE)

if df.empty:
    print("No hay resultados para optimizar.")
    exit()

validated = df[df["Result"].isin(["Winner", "Loser"])]

if validated.empty:
    print("Todavía no hay Winners/Losers suficientes.")
    exit()

weights = {
    "smart_money_bonus": 10,
    "conviction_bonus": 10,
    "opportunity_bonus": 10,
    "risk_penalty": -10,
}

if "AI Conviction" in validated.columns:

    conviction_stats = (
        validated.groupby("AI Conviction")["PnL %"]
        .mean()
    )

    if (
        "🟢 Extreme Conviction" in conviction_stats
        and conviction_stats["🟢 Extreme Conviction"] > 0
    ):
        weights["conviction_bonus"] += 10

if "Opportunity Type" in validated.columns:

    opportunity_stats = (
        validated.groupby("Opportunity Type")["PnL %"]
        .mean()
    )

    if len(opportunity_stats) > 0:

        weights["best_opportunity_type"] = (
            opportunity_stats.idxmax()
        )

        weights["best_opportunity_avg_pnl"] = round(
            opportunity_stats.max(),
            2
        )

if "Market Sentiment" in validated.columns:

    sentiment_stats = (
        validated.groupby("Market Sentiment")["PnL %"]
        .mean()
    )

    if len(sentiment_stats) > 0:

        weights["best_market_sentiment"] = (
            sentiment_stats.idxmax()
        )

        weights["best_sentiment_avg_pnl"] = round(
            sentiment_stats.max(),
            2
        )

with open(
    OPTIMIZED_WEIGHTS_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        weights,
        f,
        indent=4,
        ensure_ascii=False
    )

print(
    "✅ Pesos optimizados guardados en "
    "config/optimized_ai_weights.json"
)

print(weights)