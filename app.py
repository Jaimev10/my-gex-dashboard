import streamlit as st
import pandas as pd
import flashalpha
import plotly.graph_objects as go
from datetime import datetime
import io

st.set_page_config(layout="wide", page_title="GEX Heatmap", initial_sidebar_state="collapsed")

YOUR_FLASHALPHA_KEY = st.secrets["FLASHALPHA_KEY"]

# ====================== THEME ======================
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
theme = st.sidebar.radio("Theme", ["Dark", "Light"], horizontal=True, index=0 if st.session_state.theme == "dark" else 1)
st.session_state.theme = theme.lower()

# ====================== GLOBAL BIAS ======================
st.markdown(f"""
<div style="text-align:center; padding:15px; border-radius:12px; background:#1a3c1a; color:#00ff88; font-size:1.5em; font-weight:bold; margin-bottom:10px;">
    🌍 OVERALL MARKET BIAS: <span style="color:#00ff88;">🟢 STRONGLY BULLISH</span>
</div>
""", unsafe_allow_html=True)

st.title("🚀 Your GEX Heatmap Tool - Full Chain")

# ====================== WATCHLIST ======================
st.sidebar.header("Watchlist")
watchlist = st.sidebar.multiselect("Select Tickers", ["SPX", "SPY", "QQQ", "IWM", "NDX"], default=["SPX", "SPY", "QQQ"])

# ====================== QUICK PRESETS & OPTIONS ======================
st.sidebar.header("Quick Actions")
compare_mode = st.sidebar.checkbox("Compare 0DTE vs 1DTE", value=False)
mobile_layout = st.sidebar.checkbox("Mobile-first vertical layout", value=False)

# ====================== REALTIME REFRESH ======================
if "last_update" not in st.session_state:
    st.session_state.last_update = datetime.now()
if "previous_gex" not in st.session_state:
    st.session_state.previous_gex = {}

col_r, col_t = st.columns([1, 4])
with col_r:
    if st.button("🔄 Refresh Now", type="primary", use_container_width=True):
        st.session_state.last_update = datetime.now()
        st.cache_data.clear()
        st.rerun()

with col_t:
    seconds_ago = int((datetime.now() - st.session_state.last_update).total_seconds())
    st.caption(f"**Live • Last updated {seconds_ago} seconds ago**")

# ====================== FILTERS ======================
st.sidebar.header("Filters")
range_percent = st.sidebar.slider("Strike range ± % of spot", 5, 30, 12)
show_all = st.sidebar.checkbox("Show ALL strikes", value=False)
min_gex_k = st.sidebar.slider("Min |GEX| ($k)", 0, 500, 50, step=25)
pos_only = st.sidebar.checkbox("Positive GEX only")
neg_only = st.sidebar.checkbox("Negative GEX only")
min_vol = st.sidebar.slider("Min Volume", 0, 10000, 100, step=100)
min_oi = st.sidebar.slider("Min OI", 0, 50000, 500, step=500)

# ====================== HELPER FUNCTIONS ======================
def get_pinning_sentiment(df, spot):
    if df.empty or spot is None:
        return "Neutral", "⚪", "gray"
    king_pos = df.loc[df["net_gex"].idxmax()] if not df.empty else None
    total_gex = df["net_gex"].sum()
    if king_pos is None:
        return "Neutral", "⚪", "gray"
    dist = abs(king_pos["strike"] - spot)
    if total_gex > 0 and dist < 30:
        return "Bullish Pin", "🟢", "green"
    elif total_gex < 0 and dist < 30:
        return "Bearish Pin", "🔴", "red"
    elif king_pos["strike"] < spot - 10:
        return "Bullish Bias", "🟢", "green"
    elif king_pos["strike"] > spot + 10:
        return "Bearish Bias", "🔴", "red"
    return "Neutral / Choppy", "⚪", "gray"

@st.cache_data(ttl=20)
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
        st.error(f"{ticker}: {e}")
        return pd.DataFrame(), None, None

# ====================== MAIN DASHBOARD ======================
if mobile_layout:
    for ticker in watchlist:
        st.subheader(ticker)
        df, spot, gamma_flip = fetch_gex(ticker)
        # (vertical mobile rendering - simplified for now)
else:
    cols = st.columns(len(watchlist))
    for i, ticker in enumerate(watchlist):
        with cols[i]:
            df, spot, gamma_flip = fetch_gex(ticker)
            
            st.subheader(f"{ticker} — {datetime.now().strftime('%H:%M:%S')}")
            
            if df.empty or spot is None:
                st.write("No data")
                continue

            sentiment, emoji, color = get_pinning_sentiment(df, spot)
            st.markdown(f"**GEX Pinning:** <span style='color:{color}; font-size:1.2em'>{emoji} {sentiment}</span>", unsafe_allow_html=True)

            # GEX Delta
            current_total = df["net_gex"].sum()
            prev_total = st.session_state.previous_gex.get(ticker, current_total)
            delta = current_total - prev_total
            st.metric("**Total Net GEX**", f"${current_total/1_000_000:,.1f}M", 
                      delta=f"{delta/1_000_000:+.1f}M")
            st.session_state.previous_gex[ticker] = current_total

            # Apply filters
            filtered_df = df.copy()
            if not show_all and spot:
                lower = spot * (1 - range_percent / 100)
                upper = spot * (1 + range_percent / 100)
                filtered_df = filtered_df[(filtered_df["strike"] >= lower) & (filtered_df["strike"] <= upper)]
            filtered_df = filtered_df[abs(filtered_df["net_gex"]) / 1000 >= min_gex_k]
            if pos_only:
                filtered_df = filtered_df[filtered_df["net_gex"] > 0]
            if neg_only:
                filtered_df = filtered_df[filtered_df["net_gex"] < 0]
            filtered_df = filtered_df[(filtered_df["volume"] >= min_vol) & (filtered_df["open_interest"] >= min_oi)]

            def get_color(val):
                if val > 0:
                    intensity = min(255, int(70 + 185 * (val / filtered_df["net_gex"].max() if filtered_df["net_gex"].max() != 0 else 1)))
                    return f"rgb(0, {intensity}, {intensity})"
                else:
                    intensity = min(255, int(70 + 185 * (abs(val) / abs(filtered_df["net_gex"].min()) if filtered_df["net_gex"].min() != 0 else 1)))
                    return f"rgb({intensity
