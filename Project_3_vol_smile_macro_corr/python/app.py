import streamlit as st
import pandas as pd
from model import bs_price,implied_vol,delta_25_quotes,macro_correlations,lagged_vol_strategy,example_data

st.set_page_config(page_title="Vol Smile & Macro Correlation",layout="wide")
st.title("Volatility Smile & Macro Correlation Analytics")
st.caption("Synthetic macro data and illustrative backtest; no transaction costs")
a,b,c=st.columns(3)
atm=a.slider("ATM implied volatility",0.05,0.8,0.23)
call=b.slider("25Δ call implied volatility",0.05,0.8,0.22)
put=c.slider("25Δ put implied volatility",0.05,0.8,0.27)
quotes=delta_25_quotes(atm,call,put)
p,q=st.columns(2)
p.metric("25Δ Risk reversal",f"{100*quotes['risk_reversal_25d']:.2f} vol pts")
q.metric("25Δ Butterfly",f"{100*quotes['butterfly_25d']:.2f} vol pts")
st.line_chart(pd.DataFrame({"implied_volatility":[put,atm,call]},index=["25Δ put","ATM","25Δ call"]))
upload=st.file_uploader("Import macro data: date,energy_price,inflation_yoy,rate_10y",type="csv")
df=pd.read_csv(upload,parse_dates=["date"]) if upload else example_data()
try:
    corr=macro_correlations(df)
    bt=lagged_vol_strategy(df)
    st.subheader("Rolling energy–macro correlations (30 observations)")
    st.line_chart(corr.set_index("date")[["energy_vs_inflation_corr","energy_vs_rates_corr"]])
    st.subheader("No-look-ahead illustrative regime backtest")
    st.line_chart(bt.set_index("date")[["strategy_equity","buy_hold_equity"]])
    st.dataframe(bt.tail(12),use_container_width=True)
except (ValueError,KeyError) as e:
    st.error(f"Data issue: {e}")
