import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="J-AI Performance Dashboard",
    layout="wide"
)

st.title("📊 J-AI Performance Analytics")

try:
    df = pd.read_csv("analytics/trade_outcomes.csv")

except Exception as e:
    st.error(f"Error loading outcomes: {e}")
    st.stop()

if len(df) == 0:

    st.title("📊 J-AI Performance Dashboard")

    st.info("🕒 Mercado fuera de horario o todavía no hay suficientes datos.")

    st.markdown("""
    ### Estado actual del sistema

    ✅ Scanner IA funcionando  
    ✅ Trade tracker funcionando  
    ✅ Learning engine activo  

    ⏳ Esperando movimiento real de mercado para generar:
    - Winners
    - Losers
    - Winrate
    - PnL
    - Estadísticas IA
    """)

    st.stop()

col1, col2, col3, col4 = st.columns(4)

total_trades = len(df)

winners = len(df[df["Result"] == "Winner"])

losers = len(df[df["Result"] == "Loser"])

winrate = (
    winners / total_trades
) * 100 if total_trades > 0 else 0

average_pnl = df["PnL %"].mean()

if winners == 0 and losers == 0:

    st.info("""
    🕒 Mercado fuera de horario o todavía no hay movimiento suficiente.

    El sistema ya tiene señales guardadas, pero aún no hay operaciones marcadas como Winner o Loser.

    ⏳ Esperando movimiento real de mercado para generar:
    - Winners
    - Losers
    - Winrate real
    - PnL real
    """)

col1.metric("📈 Total Trades", total_trades)
col2.metric("🏆 Winners", winners)
col3.metric("📉 Losers", losers)
col4.metric("🎯 Winrate", f"{winrate:.2f}%")

st.metric(
    "💰 Average PnL",
    f"{average_pnl:.2f}%"
)

st.subheader("📋 Trade Outcomes")

st.dataframe(
    df.tail(100),
    use_container_width=True
)

if "Opportunity Type" in df.columns:

    st.subheader("🔥 Opportunity Type Performance")

    opportunity_stats = (
        df.groupby("Opportunity Type")["PnL %"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    st.dataframe(
        opportunity_stats,
        use_container_width=True
    )

if "AI Conviction" in df.columns:

    st.subheader("🧠 AI Conviction Performance")

    conviction_stats = (
        df.groupby("AI Conviction")["PnL %"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    st.dataframe(
        conviction_stats,
        use_container_width=True
    )
import time

time.sleep(60)
st.rerun()