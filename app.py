import streamlit as st
import pandas as pd
import flashalpha
import plotly.graph_objects as go
from datetime import datetime, date, timedelta

st.set_page_config(layout="wide", page_title="GEX Heatmap")
st.title("🚀 Your GEX Heatmap Tool (SPX / SPY / QQQ)")

YOUR_FLASHALPHA_KEY = st.secrets["FLASHALPHA_KEY"]

# Quick expiration buttons
st.sidebar.header("Quick Expirations")
col1, col2, col3, col4 = st.sidebar.columns(4)
today = date.today()

if col1.button("0DTE", use_container_width=True):
    selected_date = today
elif col2.button("1DTE", use_container_width=True):
    selected_date = today + timedelta(days=1)
elif col3.button("2DTE", use_container_width=True):
    selected_date = today + timedelta(days=2)
elif col4.button("Weekly", use_container_width=True):
    days_ahead = (4 - today.weekday()) % 7
    if days_ahead == 0: days_ahead = 7
    selected_date = today + timedelta(days=days_ahead)
else:
    selected_date = st.sidebar.date_input("Or pick any date", value=today)

expiration_str = selected_date.strftime("%Y-%m-%d")
st.sidebar.caption(f"**Using:** {expiration_str}")

# Strike range filter (what you asked for)
st.sidebar.header("Strike Filter")
range_percent = st.sidebar.slider("Show strikes within ± % of spot", 
                                 min_value=5, max_value=30, value=12, step=1)
show_all = st.sidebar.checkbox("Show ALL strikes", value=False)

@st.cache_data(ttl=30)
def fetch_gex(ticker, expiration):
    fa = flashalpha.FlashAlpha(api_key=YOUR_FLASHALPHA_KEY)
    try:
        data = fa.gex(ticker, expiration=expiration)
        spot = data.get("underlying_price")
        gamma_flip = data.get("gamma_flip")
        strikes = data.get("strikes", [])
        df = pd.DataFrame(strikes)
        if not df.empty:
            df = df.sort_values("strike")
            df["net_gex"] = df["net_gex"].fillna(0)
        return df, spot, gamma_flip
    except Exception as e:
        st.error(f"Oops! {ticker} said: {e}")
        return pd.DataFrame(), None, None

cols = st.columns(3)
tickers = ["SPX", "SPY", "QQQ"]

for i, ticker in enumerate(tickers):
    with cols[i]:
        df, spot, gamma_flip = fetch_gex(ticker, expiration_str)
        
        st.subheader(f"{ticker} — {datetime.now().strftime('%H:%M:%S')} — {expiration_str}")
        
        if df.empty:
            st.write("No data for this expiration")
            continue

        # Apply strike filter
        if not show_all and spot is not None:
            lower = spot * (1 - range_percent / 100)
            upper = spot * (1 + range_percent / 100)
            df = df[(df["strike"] >= lower) & (df["strike"] <= upper)].copy()

        total_gex = df["net_gex"].sum()
        st.metric("**Total Net GEX**", f"${total_gex/1_000_000:,.1f}M", 
                  delta=f"Flip: ${gamma_flip:,.0f}" if gamma_flip else None)

        # Colors tuned to look very close to your screenshot
        def get_color(val):
            if val > 0:
                intensity = min(255, int(70 + 185 * (val / df["net_gex"].max() if df["net_gex"].max() != 0 else 1)))
                return f"rgb(0, {intensity}, {intensity})"
            else:
                intensity = min(255, int(70 + 185 * (abs(val) / abs(df["net_gex"].min()) if df["net_gex"].min() != 0 else 1)))
                return f"rgb({intensity}, 20, {intensity})"

        king_pos = df.loc[df["net_gex"].idxmax()] if not df.empty else None
        king_neg = df.loc[df["net_gex"].idxmin()] if not df.empty else None

        fig = go.Figure(data=[go.Table(
            header=dict(
                values=["Strike", "Vol", "OI", "GEX ($k)"],
                align="center",
                font=dict(size=14, color="white"),
                height=40
            ),
            cells=dict(
                values=[
                    df["strike"].round(0),
                    df.get("volume", ["-"] * len(df)),
                    df.get("open_interest", ["-"] * len(df)),
                    (df["net_gex"]/1000).round(1)
                ],
                align="center",
                font=dict(size=13),
                fill_color=[["#1a1a2e"] + [get_color(v) for v in df["net_gex"]]],
                height=32,
                line_color=[[
                    "#ffd700" if king_pos is not None and s == king_pos["strike"] else
                    "#c724c7" if king_neg is not None and s == king_neg["strike"] else
                    "#ffffff" for s in df["strike"]
                ]]
            )
        )])
        
        fig.update_layout(height=780, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

        if king_pos is not None:
            st.success(f"**King +** {king_pos['strike']} (+${king_pos['net_gex']/1_000_000:,.1f}M)")
        if king_neg is not None:
            st.error(f"**King -** {king_neg['strike']} (-${abs(king_neg['net_gex'])/1_000_000:,.1f}M)")

st.caption("💡 Use sidebar to change expiration or strike range • Auto-updates every 30 seconds")
