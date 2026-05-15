import streamlit as st
import pandas as pd
import flashalpha
import plotly.graph_objects as go
from datetime import datetime, date, timedelta

st.set_page_config(layout="wide", page_title="GEX Heatmap", initial_sidebar_state="collapsed")

st.title("🚀 GEX Heatmap Tool")

YOUR_FLASHALPHA_KEY = st.secrets["FLASHALPHA_KEY"]

# Quick expiration buttons (compact)
st.sidebar.header("Expiration")
col1, col2, col3, col4 = st.sidebar.columns(4)
today = date.today()

if col1.button("0DTE", use_container_width=True):
    selected_date = today
elif col2.button("1DTE", use_container_width=True):
    selected_date = today + timedelta(days=1)
elif col3.button("2DTE", use_container_width=True):
    selected_date = today + timedelta(days=2)
elif col4.button("Weekly", use_container_width=True):
    days = (4 - today.weekday()) % 7
    if days == 0: days = 7
    selected_date = today + timedelta(days=days)
else:
    selected_date = st.sidebar.date_input("Pick date", value=today)

expiration_str = selected_date.strftime("%Y-%m-%d")

@st.cache_data(ttl=30)
def fetch_gex(ticker, expiration):
    fa = flashalpha.FlashAlpha(api_key=YOUR_FLASHALPHA_KEY)
    try:
        data = fa.gex(ticker, expiration=expiration)
        spot = data.get("underlying_price")
        strikes = data.get("strikes", [])
        df = pd.DataFrame(strikes)
        if not df.empty:
            df = df.sort_values("strike")
        return df, spot
    except Exception as e:
        st.error(f"{ticker}: {e}")
        return pd.DataFrame(), None

cols = st.columns(3)
tickers = ["SPX", "SPY", "QQQ"]

for i, ticker in enumerate(tickers):
    with cols[i]:
        df, spot = fetch_gex(ticker, expiration_str)
        
        if spot:
            st.subheader(f"{ticker} — ${spot:,.2f}")
        else:
            st.subheader(ticker)
        
        st.caption(f"{expiration_str} | {datetime.now().strftime('%H:%M:%S')}")

        if df.empty:
            st.write("No data")
            continue

        # King levels
        king_pos = df.loc[df["net_gex"].idxmax()] if not df.empty else None
        king_neg = df.loc[df["net_gex"].idxmin()] if not df.empty else None

        # Color function - tuned to match your screenshot
        def get_color(val):
            if val > 0:
                intensity = min(255, int(70 + 185 * (val / df["net_gex"].max())))
                return f"rgb(0, {intensity}, {intensity})"   # teal → green
            else:
                intensity = min(255, int(70 + 185 * (abs(val) / abs(df["net_gex"].min()))))
                return f"rgb({intensity}, 20, {intensity})"   # purple

        fig = go.Figure(data=[go.Table(
            header=dict(
                values=["Strike", "GEX ($k)"],
                align="center",
                font=dict(size=14, color="white"),
                height=38
            ),
            cells=dict(
                values=[
                    df["strike"].round(0),
                    (df["net_gex"]/1000).round(1)
                ],
                align="center",
                font=dict(size=13),
                fill_color=[["#0f172a"] + [get_color(v) for v in df["net_gex"]]],
                height=32,
                line_color=[[
                    "#ffd700" if king_pos is not None and s == king_pos["strike"] else
                    "#c026d3" if king_neg is not None and s == king_neg["strike"] else
                    "rgba(255,255,255,0.1)" for s in df["strike"]
                ]]
            )
        )])

        fig.update_layout(height=820, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

        # King labels (like your screenshot)
        if king_pos is not None:
            st.success(f"**King +** {king_pos['strike']}  (+${king_pos['net_gex']/1_000_000:,.1f}M)")
        if king_neg is not None:
            st.error(f"**King -** {king_neg['strike']}  (-${abs(king_neg['net_gex'])/1_000_000:,.1f}M)")
