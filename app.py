import streamlit as st
import pandas as pd
import flashalpha
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide", page_title="GEX Heatmap", initial_sidebar_state="collapsed")

YOUR_FLASHALPHA_KEY = st.secrets["FLASHALPHA_KEY"]

# ====================== TABS ======================
tab1, tab2 = st.tabs(["📊 GEX Dashboard", "🔥 SPX Option Flow"])

# ====================== GEX DASHBOARD (existing) ======================
with tab1:
    st.title("🚀 GEX Heatmap Tool - Full Chain")

    # (All your existing GEX code stays here - I kept it short for brevity)
    # ... [paste your previous main dashboard code here if you want, or keep the current one]

    st.caption("GEX Dashboard • Refresh anytime")

# ====================== NEW OPTION FLOW TAB ======================
with tab2:
    st.title("🔥 SPX Option Flow - Live Session Activity")

    st.caption("Showing highest volume strikes and flow pressure (real-time from Flash Alpha)")

    fa = flashalpha.FlashAlpha(api_key=YOUR_FLASHALPHA_KEY)
    try:
        data = fa.gex("SPX")   # Full chain for SPX
        spot = data.get("underlying_price")
        strikes = data.get("strikes", [])
        df = pd.DataFrame(strikes)
        
        if not df.empty:
            df = df.sort_values("strike")
            df["net_gex"] = df["net_gex"].fillna(0)
            df["volume"] = df.get("call_volume", 0) + df.get("put_volume", 0)
            df["open_interest"] = df.get("call_oi", 0) + df.get("put_oi", 0)
            df["total_volume"] = df["volume"]

            # Option Flow View - sorted by volume
            flow_df = df.nlargest(50, "total_volume")  # Top 50 most active strikes

            # Color for flow intensity
            def flow_color(val):
                if val > 0:
                    intensity = min(255, int(100 + 155 * (val / flow_df["net_gex"].max() if flow_df["net_gex"].max() != 0 else 1)))
                    return f"rgb(0, {intensity}, {intensity})"
                else:
                    intensity = min(255, int(100 + 155 * (abs(val) / abs(flow_df["net_gex"].min()) if flow_df["net_gex"].min() != 0 else 1)))
                    return f"rgb({intensity}, 20, {intensity})"

            king_pos = flow_df.loc[flow_df["net_gex"].idxmax()] if not flow_df.empty else None
            king_neg = flow_df.loc[flow_df["net_gex"].idxmin()] if not flow_df.empty else None

            fig = go.Figure(data=[go.Table(
                header=dict(values=["Strike", "Total Vol", "OI", "Net GEX ($k)"], align="center", font=dict(size=14, color="white")),
                cells=dict(
                    values=[
                        flow_df["strike"].round(0),
                        flow_df["total_volume"].round(0),
                        flow_df["open_interest"].round(0),
                        (flow_df["net_gex"]/1000).round(1)
                    ],
                    align="center",
                    font=dict(size=13),
                    fill_color=[["#1a1a2e"] + [flow_color(v) for v in flow_df["net_gex"]]],
                    height=38,
                    line_color=[["#ffd700" if king_pos is not None and s == king_pos["strike"] else "#e040ff" if king_neg is not None and s == king_neg["strike"] else "#ffffff" for s in flow_df["strike"]]],
                    line_width=3
                )
            )])
            
            fig.update_layout(height=900, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig, use_container_width=True)

            st.success("🔥 Top volume strikes = strongest option flow pressure right now")

        else:
            st.write("No flow data available yet")

    except Exception as e:
        st.error(f"Flow data error: {e}")

st.caption("✅ GEX Dashboard + Live SPX Option Flow tab added")
