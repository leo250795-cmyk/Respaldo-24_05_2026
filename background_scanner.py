import json
import time
import pandas as pd
import yfinance as yf

from config.market_universe import TICKERS, DISCOVERY_LIST
from engines.scoring_engine import calculate_opportunity_score

try:
    with open("config/optimized_ai_weights.json", "r", encoding="utf-8") as f:
        optimized_weights = json.load(f)
except FileNotFoundError:
    optimized_weights = {
        "smart_money_bonus": 10,
        "conviction_bonus": 10,
        "opportunity_bonus": 10,
        "risk_penalty": -10,
    }

ALL_TICKERS = list(set(TICKERS + DISCOVERY_LIST))

print("🚀 Background Scanner iniciado...")

while True:
    signals = []

    for ticker in ALL_TICKERS:
        try:
            stock = yf.Ticker(ticker)

            hist = stock.history(
                period="1d",
                interval="5m",
                prepost=True
            )

            if len(hist) < 20:
                continue

            current_price = hist["Close"].iloc[-1]
            previous_price = hist["Close"].iloc[-2]

            volume = hist["Volume"].sum()
            avg_volume = hist["Volume"].tail(20).mean()
            current_volume = hist["Volume"].iloc[-1]

            change_percent = ((current_price - previous_price) / previous_price) * 100
            rvol = current_volume / avg_volume if avg_volume > 0 else 0

            ai_signal = "No Signal"
            autonomous_rank = 0

            if change_percent > 2 and rvol >= 3:
                ai_signal = "🚀 Strong Runner Alert"
                autonomous_rank += 80
            elif change_percent > 1 and rvol >= 2:
                ai_signal = "🔥 Momentum Alert"
                autonomous_rank += 50

            if rvol >= 5:
                autonomous_rank += 10

            if change_percent >= 5:
                autonomous_rank += 10

            autonomous_rank = min(autonomous_rank, 100)

            sector = "Other"

            if ticker in ["NVDA", "AMD", "SMCI", "MU", "NVTS", "ARM", "AVGO", "MRVL", "TSM"]:
                sector = "Semiconductors"
            elif ticker in ["QUBT", "QBTS", "RGTI", "IONQ"]:
                sector = "Quantum"
            elif ticker in ["PLTR", "AI", "BBAI", "SOUN", "PATH", "SNOW", "DDOG"]:
                sector = "AI Software"
            elif ticker in ["RKLB", "ASTS", "LUNR", "ACHR", "JOBY"]:
                sector = "Space"
            elif ticker in ["SMR", "OKLO", "NNE", "EOSE", "CEG", "VST"]:
                sector = "Energy/Nuclear"
            elif ticker in ["MSTR", "COIN", "MARA", "RIOT", "IREN", "HOOD"]:
                sector = "High Beta"
            elif ticker in ["TSLA"]:
                sector = "EV"

            market_leader = "No"

            if autonomous_rank >= 80 and rvol >= 3 and change_percent >= 3:
                market_leader = "🔥 Market Leader"
            elif autonomous_rank >= 50 and rvol >= 2:
                market_leader = "⚡ Sector Leader"

            sector_rotation_signal = "Neutral"

            if sector == "Quantum" and rvol >= 3:
                sector_rotation_signal = "⚛️ Quantum Rotation"
            elif sector == "Semiconductors" and change_percent >= 2:
                sector_rotation_signal = "🔥 Semi Rotation"
            elif sector == "AI Software" and autonomous_rank >= 50:
                sector_rotation_signal = "🤖 AI Rotation"
            elif sector == "Energy/Nuclear" and rvol >= 2:
                sector_rotation_signal = "⚡ Energy Rotation"

            institutional_signal = "Neutral"

            if rvol >= 5 and change_percent >= 3:
                institutional_signal = "🏦 Institutional Buying"
            elif rvol >= 3 and change_percent > 0:
                institutional_signal = "📈 Accumulation"
            elif change_percent < -2 and rvol >= 3:
                institutional_signal = "📉 Distribution"

            opportunity_score = calculate_opportunity_score(
                autonomous_rank,
                rvol,
                change_percent,
                market_leader,
                sector_rotation_signal
            )

            if institutional_signal == "🏦 Institutional Buying":
                opportunity_score += optimized_weights.get("smart_money_bonus", 10)

            if autonomous_rank >= 80:
                opportunity_score += optimized_weights.get("opportunity_bonus", 10)

            if rvol < 1:
                opportunity_score += optimized_weights.get("risk_penalty", -10)

            opportunity_score = min(max(opportunity_score, 0), 100)

            smart_money_signal = "Neutral"

            if (
                institutional_signal == "🏦 Institutional Buying"
                and opportunity_score >= 80
                and market_leader == "🔥 Market Leader"
            ):
                smart_money_signal = "🐋 Smart Money Detected"
            elif (
                institutional_signal == "📈 Accumulation"
                and sector_rotation_signal != "Neutral"
            ):
                smart_money_signal = "🧠 Early Smart Money"
            elif rvol >= 5 and change_percent >= 5:
                smart_money_signal = "🚨 Unusual Activity"

            opportunity_type = "Neutral"

            if smart_money_signal == "🐋 Smart Money Detected" and autonomous_rank >= 80:
                opportunity_type = "🏦 Institutional Momentum"
            elif ai_signal == "🚀 Strong Runner Alert" and rvol >= 5:
                opportunity_type = "💥 Explosive Squeeze"
            elif sector_rotation_signal != "Neutral" and autonomous_rank >= 50:
                opportunity_type = "🔄 Sector Rotation Momentum"
            elif change_percent >= 1 and rvol >= 2:
                opportunity_type = "⚡ Intraday Momentum"
            elif rvol >= 5:
                opportunity_type = "🎯 Speculative Volume Spike"

            entry_price = round(current_price, 2)
            stop_loss = round(current_price * 0.97, 2)

            target_1 = round(current_price * 1.03, 2)
            target_2 = round(current_price * 1.06, 2)
            target_3 = round(current_price * 1.10, 2)

            trade_plan = "No Trade"

            if opportunity_type == "🏦 Institutional Momentum":
                trade_plan = "🚀 Aggressive Momentum Plan"
            elif opportunity_type == "💥 Explosive Squeeze":
                trade_plan = "💥 High Volatility Squeeze Plan"
                target_3 = round(current_price * 1.20, 2)
            elif opportunity_type == "🔄 Sector Rotation Momentum":
                trade_plan = "🔄 Sector Rotation Trade"
            elif opportunity_type == "⚡ Intraday Momentum":
                trade_plan = "⚡ Intraday Momentum Trade"

            if smart_money_signal == "🐋 Smart Money Detected":
                target_3 = max(target_3, round(current_price * 1.15, 2))

            trade_quality = "⚪ Average"

            if (
                opportunity_score >= 80
                and smart_money_signal == "🐋 Smart Money Detected"
                and market_leader == "🔥 Market Leader"
            ):
                trade_quality = "🟢 Institutional Grade"
            elif opportunity_score >= 70 and ai_signal == "🚀 Strong Runner Alert":
                trade_quality = "🔥 High Momentum"
            elif opportunity_score >= 50:
                trade_quality = "⚡ Tradable Momentum"
            elif opportunity_score < 30:
                trade_quality = "🔴 Weak Setup"

            risk_classification = "⚪ Moderate Risk"

            if (
                trade_quality == "🟢 Institutional Grade"
                and smart_money_signal == "🐋 Smart Money Detected"
            ):
                risk_classification = "🟢 Low Risk Institutional"
            elif opportunity_type == "💥 Explosive Squeeze" and rvol >= 5:
                risk_classification = "🔴 High Volatility"
            elif opportunity_score >= 80 and autonomous_rank >= 80:
                risk_classification = "🟠 Aggressive Momentum"
            elif opportunity_score < 30:
                risk_classification = "⚫ Avoid"

            portfolio_priority = "👀 Watch"

            if (
                trade_quality == "🟢 Institutional Grade"
                and risk_classification == "🟢 Low Risk Institutional"
            ):
                portfolio_priority = "🚀 Core Position"
            elif trade_quality == "🔥 High Momentum" and opportunity_score >= 80:
                portfolio_priority = "⚡ Aggressive Trade"
            elif opportunity_type == "💥 Explosive Squeeze":
                portfolio_priority = "💥 Speculative Runner"
            elif risk_classification == "⚫ Avoid":
                portfolio_priority = "❌ Avoid"

            capital_allocation = "⚪ Small Position"

            if portfolio_priority == "🚀 Core Position":
                capital_allocation = "🟢 15% - 25% Capital"
            elif portfolio_priority == "⚡ Aggressive Trade":
                capital_allocation = "🟠 10% - 15% Capital"
            elif portfolio_priority == "💥 Speculative Runner":
                capital_allocation = "🔴 5% - 10% Capital"
            elif portfolio_priority == "❌ Avoid":
                capital_allocation = "⚫ No Allocation"

            portfolio_balance = "⚖️ Balanced"

            if sector == "Quantum" and portfolio_priority in ["🚀 Core Position", "⚡ Aggressive Trade"]:
                portfolio_balance = "⚠️ High Quantum Exposure"
            elif sector == "Semiconductors" and portfolio_priority == "🚀 Core Position":
                portfolio_balance = "🔥 Semiconductor Overweight"
            elif sector == "Energy/Nuclear" and opportunity_score >= 70:
                portfolio_balance = "⚡ Energy Rotation Exposure"
            elif risk_classification == "🔴 High Volatility":
                portfolio_balance = "🧨 Speculative Exposure"

            heatmap_signal = "⚪ Neutral"

            if sector == "Quantum" and opportunity_score >= 80:
                heatmap_signal = "⚛️ Quantum Heat"
            elif sector == "Semiconductors" and market_leader == "🔥 Market Leader":
                heatmap_signal = "🔥 Semiconductor Heat"
            elif sector == "AI Software" and smart_money_signal != "Neutral":
                heatmap_signal = "🤖 AI Capital Flow"
            elif sector == "Energy/Nuclear" and sector_rotation_signal != "Neutral":
                heatmap_signal = "⚡ Energy Rotation Heat"
            elif opportunity_score >= 90:
                heatmap_signal = "🚀 Extreme Momentum Heat"

            market_sentiment = "⚖️ Neutral"

            if (
                heatmap_signal in [
                    "⚛️ Quantum Heat",
                    "🔥 Semiconductor Heat",
                    "🚀 Extreme Momentum Heat"
                ]
                and smart_money_signal != "Neutral"
            ):
                market_sentiment = "🚀 Risk-On Momentum"
            elif institutional_signal == "🏦 Institutional Buying" and opportunity_score >= 80:
                market_sentiment = "🐋 Institutional Bullish"
            elif risk_classification == "🔴 High Volatility":
                market_sentiment = "🧨 Speculative Mania"
            elif institutional_signal == "📉 Distribution":
                market_sentiment = "📉 Risk-Off Distribution"

            ai_conviction = "⚪ Low Conviction"

            if (
                market_sentiment in ["🚀 Risk-On Momentum", "🐋 Institutional Bullish"]
                and trade_quality == "🟢 Institutional Grade"
                and smart_money_signal == "🐋 Smart Money Detected"
            ):
                ai_conviction = "🟢 Extreme Conviction"
            elif opportunity_score >= 80 and market_leader == "🔥 Market Leader":
                ai_conviction = "🔥 High Conviction"
            elif opportunity_score >= 60:
                ai_conviction = "⚡ Medium Conviction"
            elif risk_classification == "⚫ Avoid":
                ai_conviction = "🔴 Avoid Conviction"

            execution_readiness = "⏳ Wait"

            if (
                ai_conviction == "🟢 Extreme Conviction"
                and trade_quality == "🟢 Institutional Grade"
                and market_sentiment in ["🚀 Risk-On Momentum", "🐋 Institutional Bullish"]
            ):
                execution_readiness = "🚀 Ready For Execution"
            elif ai_conviction == "🔥 High Conviction" and opportunity_score >= 80:
                execution_readiness = "⚡ Near Execution"
            elif risk_classification == "🔴 High Volatility":
                execution_readiness = "🧨 High Risk Execution"
            elif risk_classification == "⚫ Avoid":
                execution_readiness = "❌ Avoid Execution"

            watchlist_status = "Normal"

            if autonomous_rank >= 80:
                watchlist_status = "🔥 High Priority Watchlist"
            elif autonomous_rank >= 50:
                watchlist_status = "⚡ Momentum Watchlist"
            elif rvol >= 2:
                watchlist_status = "👀 Watchlist Candidate"

            signals.append({
                "Ticker": ticker,
                "Price": round(current_price, 2),
                "Volume": volume,
                "Timestamp": pd.Timestamp.now(),
                "% Change": round(change_percent, 2),
                "RVOL": round(rvol, 2),
                "AI Signal": ai_signal,
                "Autonomous Rank": autonomous_rank,
                "Watchlist Status": watchlist_status,
                "Market Leader": market_leader,
                "Sector": sector,
                "Sector Rotation": sector_rotation_signal,
                "Opportunity Score": opportunity_score,
                "Institutional Signal": institutional_signal,
                "Smart Money": smart_money_signal,
                "Opportunity Type": opportunity_type,
                "Trade Plan": trade_plan,
                "Entry Price": entry_price,
                "Stop Loss": stop_loss,
                "Target 1": target_1,
                "Target 2": target_2,
                "Target 3": target_3,
                "Trade Quality": trade_quality,
                "Risk Classification": risk_classification,
                "Portfolio Priority": portfolio_priority,
                "Capital Allocation": capital_allocation,
                "Portfolio Balance": portfolio_balance,
                "Heatmap Signal": heatmap_signal,
                "Market Sentiment": market_sentiment,
                "AI Conviction": ai_conviction,
                "Execution Readiness": execution_readiness,
            })

            print(f"✅ {ticker} scanned")

        except Exception as e:
            print(f"❌ Error {ticker}: {e}")

    df = pd.DataFrame(signals)

    if len(df) > 0:
        df.to_csv(
            "logs/background_scanner.csv",
            mode="a",
            header=not pd.io.common.file_exists("logs/background_scanner.csv"),
            index=False
        )

        print(f"💾 {len(df)} señales guardadas")

    print("⏳ Esperando próximo ciclo...\n")

    time.sleep(300)