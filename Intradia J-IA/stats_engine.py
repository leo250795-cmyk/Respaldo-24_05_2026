import pandas as pd

LEARNING_FILE = "logs/j_ai_learning_dataset.csv"

df = pd.read_csv(LEARNING_FILE, on_bad_lines="skip")

if df.empty:
    print("No hay datos todavía.")
    exit()

validated = df[df["Learning Result"].isin(["Winner", "Loser"])]

if validated.empty:
    print("Todavía no hay señales cerradas como Winner o Loser.")
    exit()

total = len(validated)
winners = len(validated[validated["Learning Result"] == "Winner"])
losers = len(validated[validated["Learning Result"] == "Loser"])

win_rate = round((winners / total) * 100, 2)
avg_return = round(validated["Future Return %"].mean(), 2)

print("\n=== J-AI STATS ENGINE ===\n")
print(f"Total señales validadas: {total}")
print(f"Winners: {winners}")
print(f"Losers: {losers}")
print(f"Win Rate: {win_rate}%")
print(f"Average Return: {avg_return}%")

print("\n=== Win Rate por Sector ===\n")
sector_stats = validated.groupby("Sector")["Learning Result"].apply(
    lambda x: round((x == "Winner").mean() * 100, 2)
)
print(sector_stats.sort_values(ascending=False))

print("\n=== Promedio de Retorno por Sector ===\n")
sector_return = validated.groupby("Sector")["Future Return %"].mean().round(2)
print(sector_return.sort_values(ascending=False))

print("\n=== Promedio por Catalyst ===\n")
catalyst_stats = validated.groupby("Catalyst")["Future Return %"].mean().round(2)
print(catalyst_stats.sort_values(ascending=False))

print("\n=== Win Rate por Pattern Type ===\n")

pattern_winrate = (
    validated.groupby("Pattern Type")["Learning Result"]
    .apply(lambda x: round((x == "Winner").mean() * 100, 2))
)

print(pattern_winrate.sort_values(ascending=False))

print("\n=== Average Return por Pattern Type ===\n")

pattern_return = (
    validated.groupby("Pattern Type")["Future Return %"]
    .mean()
    .round(2)
)

print(pattern_return.sort_values(ascending=False))