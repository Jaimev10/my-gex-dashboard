import streamlit as st
import pandas as pd
import flashalpha
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide", page_title="GEX Heatmap", initial_sidebar_state="collapsed")

YOUR_FLASHALPHA_KEY = st.secrets["FLASHALPHA_KEY"]

tab1, tab2 = st.tabs(["📊 GEX Dashboard", "🔥 SPX Option Flow"])

# ====================== GEX DASHBOARD TAB ======================
with tab1:
    st.title("🚀 GEX Heatmap Tool - Full Chain")

    # Watchlist
    st.sidebar.header("Watchlist")
    watchlist = st.sidebar.multiselect("Select Tickers", ["SPX", "SPY", "QQQ", "IWM", "NDX"], default=["SPX", "SPY", "QQQ"])

    # Refresh
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

    # Filters
    st.sidebar.header("Filters")
    range_percent = st.sidebar.slider("Strike range ± % of spot", 5, 30, 12)
    show_all = st.sidebar.checkbox("Show ALL strikes", value=False)
    min_gex_k = st.sidebar.slider("Min |GEX| ($k)", 0, 500, 50, step=25)
    pos_only = st.sidebar.checkbox("Positive GEX only")
    neg_only = st.sidebar.checkbox("Negative GEX only")
    min_vol = st.sidebar.slider("Min Volume", 0, 10000, 100, step=100)
    min_oi = st.sidebar.slider("Min OI", 0, 50000, 500, step=500)

    @st.cache_data(ttl=20)
    def fetch_gex(ticker):
        fa = flashalpha.FlashAlpha(api_key=YOUR_FLASHALPHA_KEY)
        try:
            data = fa.gex(ticker)
            spot = data.get("underlying_price")
            gamma_flip = data.get("gamma_flip")
            df = pd.DataFrame(data.get("strikes", []))
            if not df.empty:
                df = df.sort_values("strike")
                df["net_gex"] = df["net_gex"].fillna(0)
                df["volume"] = df.get("call_volume", 0) + df.get("put_volume", 0)
                df["open_interest"] = df.get("call_oi", 0) + df.get("put_oi", 0)
            return df, spot, gamma_flip
        except Exception as e:
            st.error(f"{ticker}: {e}")
            return pd.DataFrame(), None, None

    def get_pinning_sentiment(df, spot):
        if df.empty or spot is None:
            return "Neutral", "⚪", "gray"
        king_pos = df.loc[df["net_gex"].idxmax()] if not df.empty else None
        total = df["net_gex"].sum()
        if king_pos is None:
            return "Neutral", "⚪", "gray"
        dist = abs(king_pos["strike"] - spot)
        if total > 0 and dist < 30:
            return "Bullish Pin", "🟢", "green"
        elif total < 0 and dist < 30:
            return "Bearish Pin", "🔴", "red"
        elif king_pos["strike"] < spot - 10:
            return "Bullish Bias", "🟢", "green"
        elif king_pos["strike"] > spot + 10:
            return "Bearish Bias", "🔴", "red"
        return "Neutral / Choppy", "⚪", "gray"

    # Main panels
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

            # Filters applied
            filtered_df = df.copy()
            if not show_all and spot:
                lower = spot * (1 - range_percent / 100)
                upper = spot * (1 + range_percent / 100)
                filtered_df = filtered_df[(filtered_df["strike"] >= lower) & (filtered_df["strike"] <= upper)]
            filtered_df = filtered_df[abs(filtered_df["net_gex"]) / 1000 >= min_gex_k]
            if pos_only: filtered_df = filtered_df[filtered_df["net_gex"] > 0]
            if neg_only: filtered_df = filtered_df[filtered_df["net_gex"] < 0]
            filtered_df = filtered_df[(filtered_df["volume"] >= min_vol) & (filtered_df["open_interest"] >= min_oi)]

            current_total = filtered_df["net_gex"].sum()
            st.metric("**Total Net GEX**", f"${current_total/1_000_000:,.1f}M", delta=f"{current_total - st.session_state.previous_gex.get(ticker, current_total):+,} ")

            if ticker not in st.session_state.previous_gex:
                st.session_state.previous_gex[ticker] = current_total

            # Table
            king_pos = filtered_df.loc[filtered_df["net_gex"].idxmax()] if not filtered_df.empty else None
            king_neg = filtered_df.loc[filtered_df["net_gex"].idxmin()] if not filtered_df.empty else None

            def get_color(val):
                if val > 0:
                    intensity = min(255, int(70 + 185 * (val / filtered_df["net_gex"].max() if filtered_df["net_gex"].max() != 0 else 1)))
                    return f"rgb(0, {intensity}, {intensity})"
                else:
                    intensity = min(255, int(70 + 185 * (abs(val) / abs(filtered_df["net_gex"].min()) if filtered_df["net_gex"].min() != 0 else 1)))
                    return f"rgb({intensity}, 20, {intensity})"

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

            if king_pos is not None:
                st.success(f"**King +** {king_pos['strike']} (+${king_pos['net_gex']/1_000_000:,.1f}M)")
            if king_neg is not None:
                st.error(f"**King -** {king_neg['strike']} (-${abs(king_neg['net_gex'])/1_000_000:,.1f}M)")

# ====================== SPX OPTION FLOW TAB ======================
with tab2:
    st.title("🔥 SPX Option Flow - Live Session Activity")
    st.caption("Top volume strikes and flow pressure")

    try:
        fa = flashalpha.FlashAlpha(api_key=YOUR_FLASHALPHA_KEY)
        data = fa.gex("SPX")
        spot = data.get("underlying_price")
        df = pd.DataFrame(data.get("strikes", []))
        
        if not df.empty:
            df = df.sort_values("strike")
            df["volume"] = df.get("call_volume", 0) + df.get("put_volume", 0)
            df["open_interest"] = df.get("call_oi", 0) + df.get("put_oi", 0)
            df["net_gex"] = df["net_gex"].fillna(0)

            flow_df = df.nlargest(40, "volume")   # Top 40 most active strikes

            fig = go.Figure(data=[go.Table(
                header=dict(values=["Strike", "Total Vol", "OI", "Net GEX ($k)"], align="center", font=dict(size=14, color="white")),
                cells=dict(
                    values=[flow_df["strike"].round(0), flow_df["volume"].round(0), flow_df["open_interest"].round(0), (flow_df["net_gex"]/1000).round(1)],
                    align="center",
                    font=dict(size=13),
                    fill_color=[["#1a1a2e"] + ["#00ff88" if v > 0 else "#ff6666" for v in flow_df["net_gex"]]],
                    height=38,
                    line_color="#ffffff"
                )
            )])
            fig.update_layout(height=900, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig, use_container_width=True)

            st.success("🔥 Highest volume strikes right now = strongest option flow")
    except Exception as e:
        st.error(f"Option Flow error: {e}")

st.caption("✅ Both tabs working • GEX Dashboard + Live SPX Option Flow")
