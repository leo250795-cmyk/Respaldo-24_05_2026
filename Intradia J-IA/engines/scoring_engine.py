def calculate_opportunity_score(
    autonomous_rank,
    rvol,
    change_percent,
    market_leader,
    sector_rotation_signal
):
    opportunity_score = 0

    if autonomous_rank >= 80:
        opportunity_score += 30

    elif autonomous_rank >= 50:
        opportunity_score += 20

    if rvol >= 5:
        opportunity_score += 25

    elif rvol >= 3:
        opportunity_score += 15

    if change_percent >= 5:
        opportunity_score += 20

    elif change_percent >= 2:
        opportunity_score += 10

    if market_leader == "🔥 Market Leader":
        opportunity_score += 20

    elif market_leader == "⚡ Sector Leader":
        opportunity_score += 10

    if sector_rotation_signal != "Neutral":
        opportunity_score += 15

    return min(opportunity_score, 100)