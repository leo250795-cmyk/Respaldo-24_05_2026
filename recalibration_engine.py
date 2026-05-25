import json
import pandas as pd

LEARNING_FILE = "logs/j_ai_learning_dataset.csv"
WEIGHTS_FILE = "config/j_ai_weights.json"

df = pd.read_csv(LEARNING_FILE, on_bad_lines="skip")

validated = df[df["Learning Result"].isin(["Winner", "Loser"])]

if validated.empty:
    print("Todavía no hay suficientes señales validadas para recalibrar.")
    exit()

weights = {
    "rvol_bonus": 10,
    "gap_bonus": 10,
    "squeeze_bonus": 15,
    "sector_bonus": 10,
    "catalyst_bonus": 10,
}

def win_rate(filter_df):
    if len(filter_df) == 0:
        return 0
    return (filter_df["Learning Result"] == "Winner").mean() * 100

if win_rate(validated[validated["RVOL"] >= 3]) >= 60:
    weights["rvol_bonus"] += 10

if win_rate(validated[validated["Gap %"] >= 5]) >= 60:
    weights["gap_bonus"] += 10

if win_rate(validated[validated["Squeeze"] == "💥 Potential Squeeze"]) >= 60:
    weights["squeeze_bonus"] += 15

sector_stats = (
    validated.groupby("Sector")["Learning Result"]
    .apply(lambda x: (x == "Winner").mean() * 100)
    .sort_values(ascending=False)
)

if not sector_stats.empty:
    weights["best_sector"] = sector_stats.index[0]
    weights["best_sector_win_rate"] = round(sector_stats.iloc[0], 2)

with open(WEIGHTS_FILE, "w") as f:
    json.dump(weights, f, indent=4)

print("✅ Pesos recalibrados guardados en config/j_ai_weights.json")
print(weights)