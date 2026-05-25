import random
import time
import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import ta
import yfinance as yf

from config.market_universe import TICKERS, DISCOVERY_LIST


with open("config/j_ai_weights.json", "r") as f:
    dynamic_weights = json.load(f)

try:
    with open("config/pattern_weights.json", "r") as f:
        pattern_weights = json.load(f)
except FileNotFoundError:
    pattern_weights = {}


def play_alert_sound():
    st.markdown(
        """
        <audio autoplay>
            <source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" type="audio/ogg">
        </audio>
        """,
        unsafe_allow_html=True
    )


HOT_LIST = [
    "NVDA", "AMD", "SMCI", "PLTR", "TSLA",
    "MU", "IONQ", "QBTS", "RGTI", "QUBT",
    "RKLB", "ASTS", "ACHR", "JOBY",
    "MSTR", "COIN", "MARA", "RIOT",
    "OKLO", "SMR", "NNE", "TEM",
    "BBAI", "AI", "SOUN", "CAVA", "NVTS",
]


st.set_page_config(page_title="J-AI Dashboard", layout="wide")
st.title("🔥 J-AI Momentum Dashboard")

with st.sidebar.expander("⚙️ Dynamic Weights"):
    st.json(dynamic_weights)

with st.sidebar.expander("🧠 Pattern Weights"):
    st.json(pattern_weights)

refresh_rate = st.sidebar.slider(
    "Refresh Rate (seconds)",
    10,
    300,
    30
)

alerts_enabled = st.sidebar.checkbox(
    "Activar alertas sonoras",
    value=True
)

st.sidebar.write(f"Auto refresh every {refresh_rate} sec")

selected_ticker = st.sidebar.selectbox(
    "Select Ticker",
    TICKERS
)

data = []

combined_tickers = list(set(TICKERS + HOT_LIST + DISCOVERY_LIST))
random.shuffle(combined_tickers)

for ticker in combined_tickers:

    try:
        stock = yf.Ticker(ticker)

        hist = stock.history(
            period="5d",
            interval="5m",
            prepost=True
        )

        hist_15m = stock.history(
            period="5d",
            interval="15m",
            prepost=True
        )

        hist_1h = stock.history(
            period="1mo",
            interval="1h",
            prepost=True
        )

        daily_hist = stock.history(period="1mo")

        if len(hist) < 20 or len(hist_15m) < 20 or len(hist_1h) < 20 or len(daily_hist) < 20:
            continue

        current_price = hist["Close"].iloc[-1]
        previous_price = hist["Close"].iloc[-2]

        is_penny_stock = current_price <= 20

        change_percent = ((current_price - previous_price) / previous_price) * 100

        momentum_acceleration = 0
        last_5_closes = hist["Close"].tail(5)

        if len(last_5_closes) >= 5:
            momentum_acceleration = last_5_closes.iloc[-1] - last_5_closes.iloc[0]

        daily_close = daily_hist["Close"]

        daily_ema20 = ta.trend.EMAIndicator(
            daily_close,
            window=20
        ).ema_indicator().iloc[-1]

        daily_trend = "Bearish"

        if current_price > daily_ema20:
            daily_trend = "Bullish"

        avg_daily_volume = daily_hist["Volume"].tail(20).mean()
        current_volume = hist["Volume"].sum()

        if avg_daily_volume == 0:
            continue

        relative_volume = current_volume / avg_daily_volume

        rsi = ta.momentum.RSIIndicator(
            hist["Close"]
        ).rsi().iloc[-1]

        vwap = ta.volume.VolumeWeightedAveragePrice(
            high=hist["High"],
            low=hist["Low"],
            close=hist["Close"],
            volume=hist["Volume"]
        ).volume_weighted_average_price().iloc[-1]

        ema9 = ta.trend.EMAIndicator(
            hist["Close"],
            window=9
        ).ema_indicator().iloc[-1]

        ema20 = ta.trend.EMAIndicator(
            hist["Close"],
            window=20
        ).ema_indicator().iloc[-1]

        ema9_15m = ta.trend.EMAIndicator(
            hist_15m["Close"],
            window=9
        ).ema_indicator().iloc[-1]

        ema20_15m = ta.trend.EMAIndicator(
            hist_15m["Close"],
            window=20
        ).ema_indicator().iloc[-1]

        ema9_1h = ta.trend.EMAIndicator(
            hist_1h["Close"],
            window=9
        ).ema_indicator().iloc[-1]

        ema20_1h = ta.trend.EMAIndicator(
            hist_1h["Close"],
            window=20
        ).ema_indicator().iloc[-1]

        score = 0
        confidence = 50

        previous_daily_close = daily_hist["Close"].iloc[-2]

        gap_percent = ((current_price - previous_daily_close) / previous_daily_close) * 100

        premarket_high = hist["High"].tail(50).max()
        breakout_signal = "No"

        if current_price > premarket_high * 0.995:
            breakout_signal = "⚡ Near Breakout"
            score += 20

        if current_price >= premarket_high * 0.98:
            score += 15

        if is_penny_stock and relative_volume > 5:
            score += 30
        elif relative_volume > 3:
            score += dynamic_weights.get("rvol_bonus", 30)
        elif relative_volume > 2:
            score += 20
        elif relative_volume > 1:
            score += 10

        if change_percent > 8:
            score += 35
        elif change_percent > 5:
            score += 25
        elif change_percent > 2:
            score += 15
        elif change_percent > 0:
            score += 5

        if 60 <= rsi <= 80:
            score += 20

        if current_price > vwap:
            score += 20

        if ema9 > ema20:
            score += 25

        if daily_trend == "Bullish":
            score += 20

        if current_price > hist["Close"].rolling(20).mean().iloc[-1]:
            score += 15

        if hist["Close"].iloc[-1] > hist["Close"].iloc[-5]:
            score += 10

        if momentum_acceleration > 0:
            score += 10

        if momentum_acceleration > current_price * 0.01:
            score += 15

        squeeze_signal = "No"

        if (
            relative_volume >= 5
            and gap_percent >= 3
            and momentum_acceleration > current_price * 0.01
        ):
            squeeze_signal = "💥 Potential Squeeze"
            score += dynamic_weights.get("squeeze_bonus", 25)

        signal = "Neutral"

        if ema9 > ema20 and current_price > vwap and relative_volume > 1.5:
            signal = "🚀 Bullish Momentum"
        elif ema9 < ema20 and current_price < vwap:
            signal = "🔻 Weakness"

        institutional_flow = "Neutral"

        if (
            relative_volume >= 5
            and momentum_acceleration > current_price * 0.01
            and current_price > vwap
        ):
            institutional_flow = "🏦 Institutional Buying"

        elif (
            relative_volume >= 3
            and ema9 > ema20
        ):
            institutional_flow = "📈 Strong Accumulation"

        elif (
            current_price < vwap
            and ema9 < ema20
        ):
            institutional_flow = "📉 Distribution"

        catalyst = "None"
        catalyst_score = 0

        if gap_percent >= 5:
            catalyst = "🔥 High Gap"
            catalyst_score += 25
        elif relative_volume >= 3:
            catalyst = "⚡ High Volume"
            catalyst_score += 20
        elif breakout_signal == "⚡ Near Breakout":
            catalyst = "🚀 Breakout Setup"
            catalyst_score += 15

        score += catalyst_score + dynamic_weights.get("catalyst_bonus", 10)

        sector = "Other"

        if ticker in ["NVDA", "AMD", "SMCI", "MU", "ARM", "AVGO", "MRVL", "TSM", "NVTS"]:
            sector = "Semiconductors"
        elif ticker in ["PLTR", "AI", "BBAI", "SOUN", "PATH", "SNOW", "DDOG"]:
            sector = "AI Software"
        elif ticker in ["IONQ", "QBTS", "RGTI", "QUBT"]:
            sector = "Quantum"
        elif ticker in ["RKLB", "ASTS", "LUNR", "JOBY"]:
            sector = "Space"
        elif ticker in ["EOSE", "SMR", "OKLO", "CEG", "VST", "NNE"]:
            sector = "Energy/Nuclear"
        elif ticker in ["TSLA"]:
            sector = "EV"
        elif ticker in ["ACHR"]:
            sector = "eVTOL"
        elif ticker in ["HOOD", "MSTR", "COIN", "IREN", "MARA", "RIOT"]:
            sector = "High Beta"

        pattern_type = "Neutral"

        if (
            relative_volume >= 5
            and squeeze_signal == "💥 Potential Squeeze"
        ):
            pattern_type = "Squeeze Runner"

        elif (
            current_price > vwap
            and ema9 > ema20
            and momentum_acceleration > 0
        ):
            pattern_type = "Trend Continuation"

        elif (
            gap_percent >= 5
            and relative_volume >= 2
        ):
            pattern_type = "Gap Momentum"

        elif (
            current_price > vwap
            and rsi >= 60
            and breakout_signal == "⚡ Near Breakout"
        ):
            pattern_type = "Breakout Setup"

        pattern_bonus = pattern_weights.get(pattern_type, 0)
        score += pattern_bonus

        sector_strength = 0

        if sector == "Quantum":
            sector_strength += 25
        elif sector == "Semiconductors":
            sector_strength += 20
        elif sector == "AI Software":
            sector_strength += 18
        elif sector == "Energy/Nuclear":
            sector_strength += 15
        elif sector == "Space":
            sector_strength += 12

        score += sector_strength

        market_regime = "⚖️ Neutral"

        if (
            relative_volume >= 5
            and squeeze_signal == "💥 Potential Squeeze"
            and sector in ["Quantum", "AI Software"]
        ):
            market_regime = "🚀 Risk-On"

        elif (
            current_price < vwap
            and ema9 < ema20
        ):
            market_regime = "🧊 Risk-Off"

        elif (
            squeeze_signal == "💥 Potential Squeeze"
            and momentum_acceleration > current_price * 0.01
        ):
            market_regime = "💥 Squeeze Environment"

        elif institutional_flow == "📉 Distribution":
            market_regime = "📉 Distribution Phase"

        regime_bonus = 0

        if market_regime == "🚀 Risk-On":
            regime_bonus += 15
        elif market_regime == "💥 Squeeze Environment":
            regime_bonus += 20
        elif market_regime == "🧊 Risk-Off":
            regime_bonus -= 15
        elif market_regime == "📉 Distribution Phase":
            regime_bonus -= 20

        score += regime_bonus

        multi_tf_alignment = "Neutral"

        if (
            ema9 > ema20
            and ema9_15m > ema20_15m
            and ema9_1h > ema20_1h
        ):
            multi_tf_alignment = "🚀 Full Bullish Alignment"
            score += 25

        elif (
            ema9 < ema20
            and ema9_15m < ema20_15m
            and ema9_1h < ema20_1h
        ):
            multi_tf_alignment = "📉 Full Bearish Alignment"

        winner_memory = "Neutral"
        winner_memory_bonus = 0

        if ticker in ["QUBT", "QBTS", "RGTI", "IONQ"]:
            winner_memory = "⚛️ Quantum Runner Histórico"
            winner_memory_bonus += 15
        elif ticker in ["NVDA", "SMCI", "AMD", "NVTS"]:
            winner_memory = "🔥 Momentum Leader Histórico"
            winner_memory_bonus += 10
        elif ticker in ["MSTR", "COIN", "MARA"]:
            winner_memory = "₿ High Beta Runner"
            winner_memory_bonus += 8

        score += winner_memory_bonus

        ticker_intelligence = "Neutral"
        ticker_bonus = 0

        if (
            ticker in ["QUBT", "QBTS", "RGTI", "IONQ"]
            and pattern_type == "Squeeze Runner"
        ):
            ticker_intelligence = "⚛️ Quantum Squeeze Specialist"
            ticker_bonus += 15

        elif (
            ticker in ["NVDA", "SMCI", "AMD", "NVTS"]
            and pattern_type == "Trend Continuation"
        ):
            ticker_intelligence = "🔥 Momentum Continuation Leader"
            ticker_bonus += 10

        elif (
            ticker in ["MSTR", "COIN", "MARA"]
            and relative_volume >= 3
        ):
            ticker_intelligence = "₿ High Beta Volatility Runner"
            ticker_bonus += 8

        score += ticker_bonus

        priority = "WATCHLIST"

        if score >= 90 and relative_volume >= 2 and gap_percent >= 2:
            priority = "🔥 PRIORITY 1"
        elif score >= 65 and relative_volume >= 1.5:
            priority = "⚡ PRIORITY 2"
        elif score >= 40:
            priority = "👀 WATCHLIST"

        if score >= 90:
            confidence += 25
        elif score >= 70:
            confidence += 15

        if squeeze_signal == "💥 Potential Squeeze":
            confidence += 10

        if relative_volume >= 5:
            confidence += 10

        if priority == "🔥 PRIORITY 1":
            confidence += 15

        confidence += regime_bonus
        confidence += winner_memory_bonus
        confidence += ticker_bonus

        if multi_tf_alignment == "🚀 Full Bullish Alignment":
            confidence += 15

        confidence = max(0, min(confidence, 100))

        decision = "❌ Evitar"

        if (
            score >= 80
            and relative_volume >= 2
            and gap_percent >= 2
            and breakout_signal == "⚡ Near Breakout"
            and current_price > vwap
            and ema9 > ema20
        ):
            decision = "🚀 Entrar con confirmación"

        elif score >= 50 and current_price > vwap and ema9 > ema20:
            decision = "⏳ Esperar pullback / confirmación"

        entry_price = round(current_price, 2)
        stop_loss = round(min(vwap, ema20) * 0.995, 2)
        target_price = round(current_price * 1.05, 2)

        target_1 = round(current_price * 1.03, 2)
        target_2 = round(current_price * 1.05, 2)
        target_3 = round(current_price * 1.08, 2)

        if market_regime == "🚀 Risk-On":
            target_2 = round(current_price * 1.08, 2)
            target_3 = round(current_price * 1.20, 2)

        elif market_regime == "💥 Squeeze Environment":
            target_3 = round(current_price * 1.30, 2)

        elif market_regime == "🧊 Risk-Off":
            target_1 = round(current_price * 1.02, 2)
            target_2 = round(current_price * 1.03, 2)
            target_3 = round(current_price * 1.05, 2)

        elif market_regime == "📉 Distribution Phase":
            target_1 = round(current_price * 1.01, 2)
            target_2 = round(current_price * 1.02, 2)
            target_3 = round(current_price * 1.03, 2)

        if squeeze_signal == "💥 Potential Squeeze":
            target_3 = max(target_3, round(current_price * 1.15, 2))

        if relative_volume >= 5:
            target_2 = max(target_2, round(current_price * 1.08, 2))
            target_3 = max(target_3, round(current_price * 1.20, 2))

        if priority == "🔥 PRIORITY 1":
            target_3 = max(target_3, round(current_price * 1.25, 2))

        risk = entry_price - stop_loss
        reward = target_2 - entry_price
        risk_reward = round(reward / risk, 2) if risk > 0 else 0

        if risk_reward >= 2 and decision != "❌ Evitar":
            decision = decision + " | RR válido"
        elif decision != "❌ Evitar":
            decision = decision + " | RR débil"

        entry_signal = "No Entry"

        if (
            decision != "❌ Evitar"
            and current_price > vwap
            and ema9 > ema20
            and relative_volume >= 1.5
            and momentum_acceleration > 0
        ):
            entry_signal = "✅ Entrada válida"

        if (
            priority == "🔥 PRIORITY 1"
            and squeeze_signal == "💥 Potential Squeeze"
        ):
            entry_signal = "🚀 Entrada agresiva"

        exit_signal = "Mantener"

        if current_price < vwap:
            exit_signal = "⚠️ Salir: perdió VWAP"
        elif ema9 < ema20:
            exit_signal = "⚠️ Salir: perdió momentum"
        elif rsi >= 85:
            exit_signal = "💰 Tomar ganancia parcial"
        elif momentum_acceleration < 0:
            exit_signal = "⚠️ Momentum desacelerando"

        trailing_stop = stop_loss

        if current_price >= target_1:
            trailing_stop = round(entry_price * 1.01, 2)

        if current_price >= target_2:
            trailing_stop = round(entry_price * 1.03, 2)

        if current_price >= target_3:
            trailing_stop = round(entry_price * 1.08, 2)

        if squeeze_signal == "💥 Potential Squeeze":
            trailing_stop = round(ema9 * 0.995, 2)

        exit_action = "Mantener posición"

        if exit_signal == "💰 Tomar ganancia parcial":
            exit_action = "Vender 30% - 50%"

        elif exit_signal in [
            "⚠️ Salir: perdió VWAP",
            "⚠️ Salir: perdió momentum"
        ]:
            exit_action = "Salir completo"

        elif current_price >= target_1 and current_price < target_2:
            exit_action = "Subir stop y vender parcial"

        elif current_price >= target_2:
            exit_action = "Asegurar ganancia fuerte"

        risk_multiplier = 1.0

        if market_regime == "🚀 Risk-On":
            risk_multiplier = 1.5
        elif market_regime == "💥 Squeeze Environment":
            risk_multiplier = 1.8
        elif market_regime == "🧊 Risk-Off":
            risk_multiplier = 0.5
        elif market_regime == "📉 Distribution Phase":
            risk_multiplier = 0.3

        position_size = "No operar"

        if entry_signal == "🚀 Entrada agresiva":
            position_size = f"Riesgo alto controlado x{risk_multiplier}: 50% - 70% de posición planeada"

        elif entry_signal == "✅ Entrada válida":
            position_size = f"Riesgo moderado x{risk_multiplier}: 30% - 50% de posición planeada"

        elif priority == "⚡ PRIORITY 2":
            position_size = f"Riesgo bajo x{risk_multiplier}: 20% - 30% de posición planeada"

        ai_alert = "No Alert"

        if (
            confidence >= 85
            and priority == "🔥 PRIORITY 1"
            and entry_signal in ["✅ Entrada válida", "🚀 Entrada agresiva"]
        ):
            ai_alert = "🚨 ALERTA FUERTE: posible entrada"

        elif (
            squeeze_signal == "💥 Potential Squeeze"
            and relative_volume >= 5
        ):
            ai_alert = "💥 ALERTA SQUEEZE"

        elif (
            institutional_flow in ["🏦 Institutional Buying", "📈 Strong Accumulation"]
            and current_price > vwap
        ):
            ai_alert = "🏦 ALERTA FLUJO INSTITUCIONAL"

        alert_rank = 0

        if ai_alert == "🚨 ALERTA FUERTE: posible entrada":
            alert_rank = 100
        elif ai_alert == "💥 ALERTA SQUEEZE":
            alert_rank = 90
        elif ai_alert == "🏦 ALERTA FLUJO INSTITUCIONAL":
            alert_rank = 80

        if confidence >= 90:
            alert_rank += 10

        if pattern_type == "Squeeze Runner":
            alert_rank += 5

        alert_rank = min(alert_rank, 100)

        alert_reason = []

        if relative_volume >= 5:
            alert_reason.append("RVOL extremo")

        if squeeze_signal == "💥 Potential Squeeze":
            alert_reason.append("Squeeze detectado")

        if momentum_acceleration > current_price * 0.01:
            alert_reason.append("Momentum acelerando")

        if current_price > vwap:
            alert_reason.append("Precio arriba de VWAP")

        if institutional_flow == "🏦 Institutional Buying":
            alert_reason.append("Posible compra institucional")

        if priority == "🔥 PRIORITY 1":
            alert_reason.append("Priority 1")

        alert_reason_text = " | ".join(alert_reason)

        historical_similarity = "No Similarity"

        if (
            pattern_type == "Squeeze Runner"
            and confidence >= 90
            and relative_volume >= 5
        ):
            historical_similarity = "🔥 Similar a setups explosivos históricos"

        elif (
            pattern_type == "Trend Continuation"
            and institutional_flow == "🏦 Institutional Buying"
        ):
            historical_similarity = "📈 Similar a continuaciones ganadoras"

        elif (
            sector == "Quantum"
            and squeeze_signal == "💥 Potential Squeeze"
        ):
            historical_similarity = "⚛️ Similar a squeezes Quantum históricos"

        similarity_bonus = 0

        if historical_similarity != "No Similarity":
            similarity_bonus += 10

        if historical_similarity == "🔥 Similar a setups explosivos históricos":
            similarity_bonus += 15

        confidence += similarity_bonus
        confidence = min(confidence, 100)

        discovery_rank = 0

        if ticker in DISCOVERY_LIST:
            discovery_rank += 10

        if relative_volume >= 3:
            discovery_rank += 15

        if squeeze_signal == "💥 Potential Squeeze":
            discovery_rank += 20

        if market_regime in ["🚀 Risk-On", "💥 Squeeze Environment"]:
            discovery_rank += 10

        if confidence >= 90:
            discovery_rank += 15

        discovery_rank = min(discovery_rank, 100)

        emerging_runner = "No"

        if (
            ticker in DISCOVERY_LIST
            and relative_volume >= 3
            and momentum_acceleration > current_price * 0.008
            and current_price > vwap
        ):
            emerging_runner = "🚀 Emerging Runner"

        if (
            discovery_rank >= 70
            and confidence >= 85
        ):
            emerging_runner = "💥 High Potential Runner"
            
        runner_probability = 0

        if relative_volume >= 3:
            runner_probability += 20

        if squeeze_signal == "💥 Potential Squeeze":
            runner_probability += 25

        if breakout_signal == "⚡ Near Breakout":
            runner_probability += 20

        if momentum_acceleration > current_price * 0.01:
            runner_probability += 15

        if market_regime in ["🚀 Risk-On", "💥 Squeeze Environment"]:
            runner_probability += 10

        if confidence >= 90:
            runner_probability += 10

        runner_probability = min(runner_probability, 100)

        entry_timing = "Neutral"

        distance_from_vwap = (
            (current_price - vwap) / vwap
        ) * 100

        if (
            current_price > vwap
            and distance_from_vwap <= 1
            and ema9 > ema20
        ):
            entry_timing = "🟢 Early Entry"

        elif (
            current_price > vwap
            and distance_from_vwap <= 3
        ):
            entry_timing = "🟡 Momentum Entry"

        elif (
            distance_from_vwap > 5
        ):
            entry_timing = "🔴 Extended / Possible FOMO"

        elif (
            current_price < ema9
        ):
            entry_timing = "⏳ Waiting Pullback"

        smart_exit = "Mantener"

        if (
            rsi >= 85
            and momentum_acceleration < 0
        ):
            smart_exit = "💥 Blow-Off Top Risk"

        elif (
            current_price < ema9
            and current_price > vwap
        ):
            smart_exit = "⚠️ Momentum weakening"

        elif (
            current_price < vwap
        ):
            smart_exit = "🚨 Exit Warning"

        elif (
            current_price >= target_2
        ):
            smart_exit = "💰 Strong Profit Zone"

        elif (
            current_price >= target_1
        ):
            smart_exit = "💵 Partial Profit Zone"

        adaptive_confidence_bonus = 0

        if runner_probability >= 80:
            adaptive_confidence_bonus += 10

        if historical_similarity != "No Similarity":
            adaptive_confidence_bonus += 5

        if entry_timing == "🟢 Early Entry":
            adaptive_confidence_bonus += 10

        elif entry_timing == "🔴 Extended / Possible FOMO":
            adaptive_confidence_bonus -= 10

        if smart_exit == "💥 Blow-Off Top Risk":
            adaptive_confidence_bonus -= 15

        if sector in ["Quantum", "Semiconductors"]:
            adaptive_confidence_bonus += 5

        confidence += adaptive_confidence_bonus

        confidence = max(0, min(confidence, 100))

        data.append({
            "Signal ID": f"{ticker}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}",
            "Sector": sector,
            "Catalyst": catalyst,
            "Catalyst Score": catalyst_score,
            "Daily Trend": daily_trend,
            "Risk/Reward": risk_reward,
            "Gap %": round(gap_percent, 2),
            "Premarket High": round(premarket_high, 2),
            "Breakout": breakout_signal,
            "Ticker": ticker,
            "Price": round(current_price, 2),
            "% Change": round(change_percent, 2),
            "RVOL": round(relative_volume, 2),
            "RSI": round(rsi, 2),
            "EMA9": round(ema9, 2),
            "EMA20": round(ema20, 2),
            "VWAP": round(vwap, 2),
            "Signal": signal,
            "Priority": priority,
            "Decision": decision,
            "Entry": entry_price,
            "Stop": stop_loss,
            "Target": target_price,
            "J-AI Score": score,
            "Penny Stock": is_penny_stock,
            "Momentum Acceleration": round(momentum_acceleration, 2),
            "Squeeze": squeeze_signal,
            "Future Price": None,
            "Future Return %": None,
            "Hit Target": None,
            "Hit Stop": None,
            "Reached +5%": None,
            "Learning Result": "Pending",
            "Entry Signal": entry_signal,
            "Exit Signal": exit_signal,
            "Target 1/3%": target_1,
            "Target 2/5%": target_2,
            "Target 3/ 8/15/20/25%": target_3,
            "Trailing Stop": trailing_stop,
            "Exit Action": exit_action,
            "Position Size": position_size,
            "Risk Multiplier": risk_multiplier,
            "Confidence": confidence,
            "Pattern Type": pattern_type,
            "Pattern Bonus": pattern_bonus,
            "Sector Strength": sector_strength,
            "Institutional Flow": institutional_flow,
            "AI Alert": ai_alert,
            "AI Alert Rank": alert_rank,
            "AI Alert Reason": alert_reason_text,
            "Historical Similarity": historical_similarity,
            "Similarity Bonus": similarity_bonus,
            "Winner Memory": winner_memory,
            "Winner Memory Bonus": winner_memory_bonus,
            "Ticker Intelligence": ticker_intelligence,
            "Ticker Bonus": ticker_bonus,
            "Market Regime": market_regime,
            "Regime Bonus": regime_bonus,
            "Adaptive Targets": market_regime,
            "Multi TF Alignment": multi_tf_alignment,
            "Discovery Rank": discovery_rank,
            "Emerging Runner": emerging_runner,
            "Runner Probability": runner_probability,
            "Entry Timing": entry_timing,
            "Smart Exit": smart_exit,
            "Adaptive Confidence Bonus": adaptive_confidence_bonus,
        })

    except Exception as e:
        st.write(f"Error con {ticker}: {e}")
        continue


df = pd.DataFrame(data)

if df.empty:
    st.warning("No se pudieron procesar acciones en este escaneo.")
    st.stop()

df = df.sort_values(by="J-AI Score", ascending=False)

signals_to_save = df[df["J-AI Score"] >= 50].copy()

if len(signals_to_save) > 0:
    signals_to_save["Scan Time"] = pd.Timestamp.now()

    signals_to_save.to_csv(
        "logs/j_ai_learning_dataset.csv",
        mode="a",
        header=not pd.io.common.file_exists("logs/j_ai_learning_dataset.csv"),
        index=False
    )

strong_setups = df[df["J-AI Score"] >= 40]

explosive_setups = df[
    (df["J-AI Score"] >= 70)
    & (df["RVOL"] >= 1.5)
    & (df["Gap %"] >= 2)
    & (df["Breakout"] == "⚡ Near Breakout")
]

st.subheader("📊 All Scanned Stocks")

styled_df = df.style.background_gradient(
    subset=["J-AI Score", "RVOL"],
    cmap="RdYlGn"
)

st.dataframe(
    styled_df,
    use_container_width=True
)

top_momentum = df.nlargest(5, "J-AI Score")

st.subheader("🔥 Top 5 Momentum")
st.dataframe(top_momentum, use_container_width=True)

top_rvol = df.nlargest(5, "RVOL")

st.subheader("📈 Top 5 RVOL")
st.dataframe(top_rvol, use_container_width=True)

top_rr = df.nlargest(5, "Risk/Reward")

st.subheader("💰 Top 5 Risk/Reward")
st.dataframe(top_rr, use_container_width=True)

st.subheader("🔥 Strong Momentum Setups")
st.dataframe(strong_setups, use_container_width=True)

st.subheader("🚀 Explosive Watchlist")
st.dataframe(explosive_setups, use_container_width=True)

ai_alerts = df[df["AI Alert"] != "No Alert"]

st.subheader("🚨 AI Alert Center")

styled_alerts = ai_alerts.style.background_gradient(
    subset=["Confidence", "J-AI Score", "RVOL"],
    cmap="RdYlGn"
)

st.dataframe(
    styled_alerts,
    use_container_width=True
)

priority_feed = df[df["AI Alert Rank"] >= 80].sort_values(
    by="AI Alert Rank",
    ascending=False
)

st.subheader("🚨 AI Priority Feed")

styled_priority_feed = priority_feed.style.background_gradient(
    subset=["AI Alert Rank", "Confidence", "J-AI Score", "RVOL"],
    cmap="RdYlGn"
)

st.dataframe(
    styled_priority_feed,
    use_container_width=True
)

discovery_feed = df[df["Discovery Rank"] >= 40].sort_values(
    by="Discovery Rank",
    ascending=False
)

st.subheader("🛰️ Discovery Feed — Runners Emergentes")

styled_discovery = discovery_feed.style.background_gradient(
    subset=["Discovery Rank", "J-AI Score", "RVOL", "Confidence"],
    cmap="RdYlGn"
)

st.dataframe(
    styled_discovery,
    use_container_width=True
)

if alerts_enabled and len(priority_feed[priority_feed["AI Alert Rank"] >= 90]) > 0:
    play_alert_sound()

st.subheader("📌 Resumen de Alertas IA")

alert_summary = (
    df.groupby("AI Alert")["Ticker"]
    .count()
    .sort_values(ascending=False)
    .reset_index()
)

alert_summary.columns = ["Tipo de alerta", "Cantidad"]

st.dataframe(
    alert_summary,
    use_container_width=True
)

priority_1 = df[df["Priority"] == "🔥 PRIORITY 1"]

st.subheader("🔥 PRIORITY 1 SETUPS")

styled_priority = priority_1.style.background_gradient(
    subset=["J-AI Score", "RVOL", "Risk/Reward"],
    cmap="RdYlGn"
)

st.dataframe(
    styled_priority,
    use_container_width=True
)

penny_setups = df[
    (df["Penny Stock"] == True)
    & (df["RVOL"] >= 2)
]

st.subheader("💥 Explosive Penny Scanner")

styled_penny = penny_setups.style.background_gradient(
    subset=["J-AI Score", "RVOL"],
    cmap="RdYlGn"
)

st.dataframe(
    styled_penny,
    use_container_width=True
)

st.subheader("🔥 Sector Momentum Ranking")

sector_ranking = (
    df.groupby("Sector")["J-AI Score"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

leader_sector = sector_ranking.iloc[0]["Sector"]

df["Sector Bonus"] = df["Sector"].apply(
    lambda x: dynamic_weights.get("sector_bonus", 15)
    if x == leader_sector else 0
)

df["J-AI Score"] = df["J-AI Score"] + df["Sector Bonus"]
df = df.sort_values(by="J-AI Score", ascending=False)

st.success(f"🔥 Sector líder del momento: {leader_sector}")

styled_sector = sector_ranking.style.background_gradient(
    subset=["J-AI Score"],
    cmap="RdYlGn"
)

st.dataframe(
    styled_sector,
    use_container_width=True
)

sector_rotation = (
    df.groupby("Sector")
    .agg({
        "J-AI Score": "mean",
        "RVOL": "mean",
        "Momentum Acceleration": "mean"
    })
    .reset_index()
)

sector_rotation["Rotation Score"] = (
    sector_rotation["J-AI Score"]
    + (sector_rotation["RVOL"] * 10)
    + (sector_rotation["Momentum Acceleration"] * 2)
)

sector_rotation = sector_rotation.sort_values(
    by="Rotation Score",
    ascending=False
)

rotation_leader = sector_rotation.iloc[0]["Sector"] if not sector_rotation.empty else None

st.subheader("🧭 Sector Rotation Engine")

st.dataframe(
    sector_rotation,
    use_container_width=True
)

rotation_leader_stocks = df[df["Sector"] == rotation_leader] if rotation_leader is not None else df.iloc[0:0]

st.subheader("🧭 Acciones del sector en rotación")

st.dataframe(
    rotation_leader_stocks,
    use_container_width=True
)

if len(strong_setups) == 0:
    st.info("Sin setups fuertes por ahora.")
else:
    st.success(f"🚀 {len(strong_setups)} setups fuertes detectados")

    if alerts_enabled and len(strong_setups[strong_setups["J-AI Score"] >= 80]) > 0:
        play_alert_sound()

    for _, row in df.head(100).iterrows():

        if row["J-AI Score"] >= 80:
            st.error(
                f"🚀 EXPLOSIVE SETUP: "
                f"{row['Ticker']} | "
                f"Score {row['J-AI Score']} | "
                f"RVOL {row['RVOL']} | "
                f"Gap {row['Gap %']}%"
            )

        elif row["J-AI Score"] >= 50:
            st.warning(
                f"🔥 Momentum fuerte: "
                f"{row['Ticker']} | "
                f"Score {row['J-AI Score']} | "
                f"RVOL {row['RVOL']}"
            )

        else:
            st.info(
                f"👀 En observación: "
                f"{row['Ticker']} | "
                f"Score {row['J-AI Score']}"
            )

st.subheader("📜 Historial de señales fuertes")

try:
    history_df = pd.read_csv(
        "logs/j_ai_learning_dataset.csv",
        on_bad_lines="skip"
    )

    st.dataframe(
        history_df.tail(50),
        use_container_width=True
    )

except FileNotFoundError:
    st.info("Aún no hay historial guardado.")

top = df.iloc[0]

chart_data = yf.download(
    selected_ticker,
    period="1d",
    interval="5m",
    prepost=True,
    progress=False
)

if len(chart_data) > 0:

    open_series = chart_data["Open"].squeeze()
    high_series = chart_data["High"].squeeze()
    low_series = chart_data["Low"].squeeze()
    close_series = chart_data["Close"].squeeze()
    volume_series = chart_data["Volume"].squeeze()

    chart_data["EMA9"] = ta.trend.EMAIndicator(
        close_series,
        window=9
    ).ema_indicator()

    chart_data["EMA20"] = ta.trend.EMAIndicator(
        close_series,
        window=20
    ).ema_indicator()

    chart_data["VWAP"] = ta.volume.VolumeWeightedAveragePrice(
        high=high_series,
        low=low_series,
        close=close_series,
        volume=volume_series
    ).volume_weighted_average_price()

    st.subheader("🚀 Top Momentum Stock")

    st.metric(
        label=top["Ticker"],
        value=f"Score: {top['J-AI Score']}",
        delta=f"RVOL: {top['RVOL']}"
    )

    if top["J-AI Score"] >= 70:
        st.success(f"🚀 HIGH MOMENTUM DETECTED: {top['Ticker']}")
    elif top["J-AI Score"] >= 50:
        st.warning(f"🔥 Momentum Building: {top['Ticker']}")

    st.write(f"Showing live data for: {selected_ticker}")
    st.header(f"📈 LIVE: {selected_ticker}")

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=chart_data.index,
        open=open_series,
        high=high_series,
        low=low_series,
        close=close_series,
        name="Price"
    ))

    fig.add_trace(go.Scatter(
        x=chart_data.index,
        y=chart_data["EMA9"],
        mode="lines",
        name="EMA 9"
    ))

    fig.add_trace(go.Scatter(
        x=chart_data.index,
        y=chart_data["EMA20"],
        mode="lines",
        name="EMA 20"
    ))

    fig.add_trace(go.Scatter(
        x=chart_data.index,
        y=chart_data["VWAP"],
        mode="lines",
        name="VWAP"
    ))

    fig.update_layout(
        height=700,
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning(f"No hay datos de gráfico para {selected_ticker}.")

time.sleep(refresh_rate)
st.rerun()