import streamlit as st
import pandas as pd
import flashalpha
import plotly.graph_objects as go
from datetime import datetime, date

st.set_page_config(layout="wide", page_title="GEX Tool")
st.title("🚀 Your GEX Heatmap Tool (SPX / SPY / QQQ)")

# ←←← Your Flash Alpha key will be stored safely in secrets (we'll set it up soon)
YOUR_FLASHALPHA_KEY = st.secrets["FLASHALPHA_KEY"]

# Sidebar for expiration date (Basic plan)
st.sidebar.header("Expiration Filter")
selected_date = st.sidebar.date_input(
    "Choose expiration date",
    value=date.today(),
    min_value=date(2024, 1, 1)
)
expiration_str = selected_date.strftime("%Y-%m-%d")

st.sidebar.caption(f"Using: **{expiration_str}**")

@st.cache_data(ttl=30)
def fetch_gex(ticker, expiration):
    fa = flashalpha.FlashAlpha(api_key=YOUR_FLASHALPHA_KEY)
    try:
        gex_data = fa.gex(ticker, expiration=expiration)
        spot = gex_data.get("underlying_price")
        strikes = gex_data.get("strikes", [])
        df = pd.DataFrame(strikes)
        df = df.sort_values("strike")
        king_pos = df.loc[df["net_gex"].idxmax()] if not df.empty else None
        king_neg = df.loc[df["net_gex"].idxmin()] if not df.empty else None
        gamma_flip = gex_data.get("gamma_flip")
        return df, spot, king_pos, king_neg, gamma_flip
    except Exception as e:
        st.error(f"Oops! {ticker} said: {e}")
        return pd.DataFrame(), None, None, None, None

cols = st.columns(3)
tickers = ["SPX", "SPY", "QQQ"]

for i, ticker in enumerate(tickers):
    with cols[i]:
        st.subheader(f"{ticker} — {datetime.now().strftime('%H:%M:%S')} — {expiration_str}")
        df, spot, king_pos, king_neg, gamma_flip = fetch_gex(ticker, expiration_str)
        
        if df.empty:
            st.write("No data for this expiration — try a different date in the sidebar")
            continue
            
        st.caption(f"Spot: **${spot:.2f}** | Gamma Flip: **${gamma_flip:.2f}**")
        
        def get_color(val):
            if val > 0:
                intensity = min(255, int(80 + 175 * (val / df["net_gex"].max())))
                return f"rgb(0, {intensity}, {intensity})"
            else:
                intensity = min(255, int(80 + 175 * (abs(val) / abs(df["net_gex"].min()))))
                return f"rgb({intensity}, 0, {intensity})"
        
        fig = go.Figure(data=[go.Table(
            header=dict(values=["Strike", "GEX ($ thousands)"], align="center", font=dict(size=14)),
            cells=dict(
                values=[df["strike"].round(0), (df["net_gex"]/1000).round(1)],
                align="center",
                font=dict(size=13),
                fill_color=[[get_color(v) for v in df["net_gex"]]],
                height=28,
                line_color=[["yellow" if king_pos is not None and s == king_pos["strike"] else 
                           "purple" if king_neg is not None and s == king_neg["strike"] else "#ffffff" 
                           for s in df["strike"]]]
            )
        )])
        fig.update_layout(height=750, margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
        if king_pos is not None:
            st.success(f"**King Positive**: {king_pos['strike']} (+${king_pos['net_gex']/1e6:.1f}M)")
        if king_neg is not None:
            st.error(f"**King Negative**: {king_neg['strike']} (-${abs(king_neg['net_gex'])/1e6:.1f}M)")

st.info("✅ Live on Streamlit Cloud • Use sidebar to change expiration")
