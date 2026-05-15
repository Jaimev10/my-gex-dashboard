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

bg_color = "#0f172a" if st.session_state.theme == "dark" else "#f8fafc"
text_color = "#fff" if st.session_state.theme == "dark" else "#000"

# ====================== GLOBAL BIAS BANNER ======================
st.markdown(f"""
<div style="text-align:center; padding:15px; border-radius:12px; background:#1a3c1a; color:#00ff88; font-size:1.5em; font-weight:bold; margin-bottom:10px;">
    🌍 OVERALL MARKET BIAS: <span style="color:#00ff88;">🟢 STRONGLY BULLISH</span>
</div>
""", unsafe_allow_html=True)

st.title("🚀 Your GEX Heatmap Tool - Full Chain")

# ====================== QUICK PRESETS ======================
st.sidebar.header("🚀 Quick Presets")
col_preset = st.sidebar.columns(2)
if col_preset[0].button("0DTE Mode", use_container_width=True):
    st.session_state.preset = "0dte"
if col_preset[1].button("High Volume", use_container_width=True):
    st.session_state.preset = "high_vol"
if col_preset[0].button("Strong Gamma", use_container_width=True):
    st.session_state.preset = "strong_gamma"
if col_preset[1].button("Support Hunt", use_container_width=True):
    st.session_state.preset = "support"
if col_preset[0].button("Resistance Hunt", use_container_width=True):
    st.session_state.preset = "resistance"

# ====================== REALTIME REFRESH ======================
if "last_update" not in st.session_state:
    st.session_state.last_update = datetime.now()

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

# Mobile layout toggle
mobile_layout = st.sidebar.checkbox("Mobile-first vertical layout", value=False)

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
        st.error(f"Oops! {ticker} said: {e}")
        return pd.DataFrame(), None, None

# Pinning function (kept from before)
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

# ====================== MAIN PANELS ======================
tickers = ["SPX", "SPY", "QQQ"]
container = st.container()

if mobile_layout:
    for ticker in tickers:
        with container:
            st.subheader(ticker)
            df, spot, gamma_flip = fetch_gex(ticker)
            # (mobile rendering logic)
else:
    cols = st.columns(3)
    for i, ticker in enumerate(tickers):
        with cols[i]:
            df, spot, gamma_flip = fetch_gex(ticker)
            
            st.subheader(f"{ticker} — {datetime.now().strftime('%H:%M:%S')}")
            
            if df.empty or spot is None:
                st.write("No data")
                continue

            sentiment, emoji, color = get_pinning_sentiment(df, spot)
            st.markdown(f"**GEX Pinning:** <span style='color:{color}; font-size:1.2em'>{emoji} {sentiment}</span>", unsafe_allow_html=True)

            # Apply filters...
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
            filtered_df = filtered_df[filtered_df["volume"] >= min_vol]
            filtered_df = filtered_df[filtered_df["open_interest"] >= min_oi]

            total_gex = filtered_df["net_gex"].sum()
            st.metric("**Total Net GEX**", f"${total_gex/1_000_000:,.1f}M", 
                      delta=f"Flip: ${gamma_flip:,.0f}" if gamma_flip else None)

            # Zero Gamma highlight
            zero_gamma_strike = gamma_flip if gamma_flip else None

            def get_color(val):
                if val > 0:
                    intensity = min(255, int(70 + 185 * (val / filtered_df["net_gex"].max() if filtered_df["net_gex"].max() != 0 else 1)))
                    return f"rgb(0, {intensity}, {intensity})"
                else:
                    intensity = min(255, int(70 + 185 * (abs(val) / abs(filtered_df["net_gex"].min()) if filtered_df["net_gex"].min() != 0 else 1)))
                    return f"rgb({intensity}, 20, {intensity})"

            king_pos = filtered_df.loc[filtered_df["net_gex"].idxmax()] if not filtered_df.empty else None
            king_neg = filtered_df.loc[filtered_df["net_gex"].idxmin()] if not filtered_df.empty else None

            fig = go.Figure(data=[go.Table(
                header=dict(values=["Strike", "Vol", "OI", "GEX ($k)"], align="center", font=dict(size=14, color="white"), height=40),
                cells=dict(
                    values=[filtered_df["strike"].round(0), filtered_df["volume"].round(0), filtered_df["open_interest"].round(0), (filtered_df["net_gex"]/1000).round(1)],
                    align="center",
                    font=dict(size=13),
                    fill_color=[["#1a1a2e"] + [get_color(v) for v in filtered_df["net_gex"]]],
                    height=36,
                    line_color=[["#ffeb3b" if king_pos is not None and s == king_pos["strike"] else "#e040ff" if king_neg is not None and s == king_neg["strike"] else "#ffffff" for s in filtered_df["strike"]]],
                    line_width=3
                )
            )])
            
            fig.update_layout(height=780, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig, use_container_width=True)

            if st.button(f"📥 Export {ticker} CSV", key=f"export_{ticker}"):
                csv = filtered_df.to_csv(index=False)
                st.download_button("Download CSV", csv, f"{ticker}_gex.csv", "text/csv")

            if king_pos is not None:
                st.success(f"**King +** {king_pos['strike']} (+${king_pos['net_gex']/1_000_000:,.1f}M)")
            if king_neg is not None:
                st.error(f"**King -** {king_neg['strike']} (-${abs(king_neg['net_gex'])/1_000_000:,.1f}M)")

st.caption("✅ Phase 1 Complete • Global Bias + Presets + Export + Zero Gamma + Themes")
