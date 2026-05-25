import json
import pandas as pd

LEARNING_FILE = "logs/j_ai_learning_dataset.csv"
PATTERN_WEIGHTS_FILE = "config/pattern_weights.json"

df = pd.read_csv(LEARNING_FILE, on_bad_lines="skip")

validated = df[df["Learning Result"].isin(["Winner", "Loser"])]

if validated.empty:
    print("Todavía no hay suficientes señales validadas para patrones.")
    exit()

pattern_stats = (
    validated.groupby("Pattern Type")["Learning Result"]
    .apply(lambda x: (x == "Winner").mean() * 100)
    .sort_values(ascending=False)
)

pattern_weights = {}

for pattern, winrate in pattern_stats.items():
    if winrate >= 70:
        pattern_weights[pattern] = 25
    elif winrate >= 60:
        pattern_weights[pattern] = 15
    elif winrate >= 50:
        pattern_weights[pattern] = 5
    else:
        pattern_weights[pattern] = 0

with open(PATTERN_WEIGHTS_FILE, "w") as f:
    json.dump(pattern_weights, f, indent=4)

print("✅ Pattern weights guardados en config/pattern_weights.json")
print(pattern_weights)