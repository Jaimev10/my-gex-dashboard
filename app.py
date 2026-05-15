import streamlit as st
import pandas as pd
import flashalpha
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide", page_title="GEX Heatmap", initial_sidebar_state="collapsed")

st.title("🚀 Your GEX Heatmap Tool (SPX / SPY / QQQ) - Full Chain")

YOUR_FLASHALPHA_KEY = st.secrets["FLASHALPHA_KEY"]

# Live timer & refresh
if "last_update" not in st.session_state:
    st.session_state.last_update = datetime.now()

col_refresh, col_time = st.columns([1, 3])
with col_refresh:
    if st.button("🔄 Refresh Now", type="primary", use_container_width=True):
        st.session_state.last_update = datetime.now()
        st.rerun()

with col_time:
    seconds_ago = int((datetime.now() - st.session_state.last_update).total_seconds())
    st.caption(f"Last updated: **{seconds_ago} seconds ago**")

# Strike range filter
st.sidebar.header("Strike Filter")
range_percent = st.sidebar.slider("Show strikes within ± % of spot", 
                                 min_value=5, max_value=30, value=12, step=1)
show_all = st.sidebar.checkbox("Show ALL strikes", value=False)

@st.cache_data(ttl=30)
def fetch_gex(ticker):
    fa = flashalpha.FlashAlpha(api_key=YOUR_FLASHALPHA_KEY)
    try:
        data = fa.gex(ticker)
        spot = data.get("underlying_price")
        gamma_flip = data.get("gamma_flip")
        strikes = data.get("strikes", [])
        df = pd.DataFrame(strikes)
        if not df.empty:
            df = df.sort_values("strike")
            df["net_gex"] = df["net_gex"].fillna(0)
            df["volume"] = df.get("call_volume", 0) + df.get("put_volume", 0)
            df["open_interest"] = df.get("call_oi", 0) + df.get("put_oi", 0)
        return df, spot, gamma_flip
    except Exception as e:
        st.error(f"Oops! {ticker} said: {e}")
        return pd.DataFrame(), None, None

cols = st.columns(3)
tickers = ["SPX", "SPY", "QQQ"]

for i, ticker in enumerate(tickers):
    with cols[i]:
        df, spot, gamma_flip = fetch_gex(ticker)
        
        st.subheader(f"{ticker} — {datetime.now().strftime('%H:%M:%S')}")
        
        if df.empty:
            st.write("No data")
            continue

        if not show_all and spot is not None:
            lower = spot * (1 - range_percent / 100)
            upper = spot * (1 + range_percent / 100)
            df = df[(df["strike"] >= lower) & (df["strike"] <= upper)].copy()

        total_gex = df["net_gex"].sum()
        st.metric("**Total Net GEX**", f"${total_gex/1_000_000:,.1f}M", 
                  delta=f"Flip: ${gamma_flip:,.0f}" if gamma_flip else None)

        # Colors
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
                    df["volume"].round(0),
                    df["open_interest"].round(0),
                    (df["net_gex"]/1000).round(1)
                ],
                align="center",
                font=dict(size=13),
                fill_color=[["#1a1a2e"] + [get_color(v) for v in df["net_gex"]]],
                height=34,
                line_color=[[
                    "#ffeb3b" if king_pos is not None and s == king_pos["strike"] else   # brighter gold
                    "#e040ff" if king_neg is not None and s == king_neg["strike"] else   # brighter purple
                    "#ffffff" for s in df["strike"]
                ]],
                line_width=3   # thicker borders for glowing effect
            )
        )])
        
        fig.update_layout(height=780, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

        if king_pos is not None:
            st.success(f"**King +** {king_pos['strike']} (+${king_pos['net_gex']/1_000_000:,.1f}M)")
        if king_neg is not None:
            st.error(f"**King -** {king_neg['strike']} (-${abs(king_neg['net_gex'])/1_000_000:,.1f}M)")

st.caption("✅ Full-chain GEX • Click Refresh Now anytime • Sidebar collapsed by default")
