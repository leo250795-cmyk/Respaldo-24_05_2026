import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Autonomous AI Dashboard",
    layout="wide"
)

st.title("🤖 Autonomous AI Trading Dashboard")

try:

    df = pd.read_csv("logs/background_scanner.csv")

except Exception as e:

    st.error(f"Error loading scanner data: {e}")
    st.stop()

if len(df) == 0:

    st.warning("No scanner data available.")
    st.stop()

st.subheader("🚀 Latest Autonomous Signals")

main_columns = [
    "Ticker",
    "Price",
    "% Change",
    "RVOL",
    "AI Signal",
    "Opportunity Score",
    "AI Conviction",
    "Execution Readiness",
    "Portfolio Priority",
]

available_columns = [
    col for col in main_columns
    if col in df.columns
]

st.dataframe(
    df[available_columns].tail(50),
    use_container_width=True
)

if "AI Conviction" in df.columns:

    conviction_feed = df[
        df["AI Conviction"].isin([
            "🟢 Extreme Conviction",
            "🔥 High Conviction"
        ])
    ]

    st.subheader("🔥 AI Conviction Feed")

    st.dataframe(
        conviction_feed.tail(20),
        use_container_width=True
    )

if "Smart Money" in df.columns:

    smart_money_feed = df[
        df["Smart Money"] != "Neutral"
    ]

    st.subheader("🐋 Smart Money Feed")

    st.dataframe(
        smart_money_feed.tail(20),
        use_container_width=True
    )

if "Execution Readiness" in df.columns:

    execution_feed = df[
        df["Execution Readiness"].isin([
            "🚀 Ready For Execution",
            "⚡ Near Execution"
        ])
    ]

    st.subheader("⚡ Execution Ready Feed")

    st.dataframe(
        execution_feed.tail(20),
        use_container_width=True
    )

if "Heatmap Signal" in df.columns:

    heatmap_feed = df[
        df["Heatmap Signal"] != "⚪ Neutral"
    ]

    st.subheader("🔥 Heatmap Feed")

    st.dataframe(
        heatmap_feed.tail(20),
        use_container_width=True
    )

if "Sector Rotation" in df.columns:

    sector_rotation = (
        df.groupby("Sector")["Opportunity Score"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    st.subheader("🧭 Sector Rotation Ranking")

    st.dataframe(
        sector_rotation,
        use_container_width=True
    )

if "Portfolio Priority" in df.columns:

    portfolio_feed = df[
        df["Portfolio Priority"] != "👀 Watch"
    ]

    st.subheader("💼 Portfolio Priority Feed")

    st.dataframe(
        portfolio_feed.tail(20),
        use_container_width=True
    )