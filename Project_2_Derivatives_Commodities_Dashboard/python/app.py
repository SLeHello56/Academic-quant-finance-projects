import streamlit as st
import pandas as pd
from model import trinomial_option, curve_metrics, example_curve

st.set_page_config(page_title="Derivatives & Commodities", layout="wide")
st.title("Derivatives & Commodities Dashboard")
st.caption("Illustrative prices and a synthetic forward curve; no live market feed")
upload=st.file_uploader("Import a commodity forward-curve CSV",type="csv")
curve=pd.read_csv(upload) if upload else example_curve()
try:
    metrics,ordered=curve_metrics(curve)
    x,y=st.columns(2)
    x.metric("Forward regime",metrics["regime"].capitalize())
    y.metric("Annualized end-to-end slope",f"{100*metrics['annualized_forward_slope']:.2f}%")
    st.line_chart(ordered.set_index("contract")["forward"])
    st.dataframe(ordered,use_container_width=True)
except (ValueError,KeyError) as e:
    st.error(f"Curve data error: {e}")
st.subheader("Trinomial tree option pricer")
c1,c2,c3,c4=st.columns(4)
s=c1.number_input("Underlying spot",min_value=1.0,value=100.0)
k=c2.number_input("Strike",min_value=1.0,value=100.0)
sigma=c3.slider("Volatility",0.05,0.9,0.25)
t=c4.slider("Time to expiry (years)",0.1,2.0,1.0)
kind=st.selectbox("Payoff",["put","call"])
exercise=st.selectbox("Exercise policy",["european","american","bermudan"])
steps=120
exercise_steps=[int(steps*tau/t) for tau in (t/4,t/2,3*t/4)] if exercise=="bermudan" else None
try:
    price=trinomial_option(s,k,t,0.03,sigma,steps,kind,exercise,exercise_steps=exercise_steps)
    st.metric("Indicative option value",f"{price:.3f}")
except ValueError as e:
    st.warning(str(e))
st.caption("Dividend/convenience yield zero, rate 3% by default. Not a tradable quote.")
