import streamlit as st
from model import gbm_paths, black_scholes, exotic_price, bumped_delta, hedge_short_call_path
import numpy as np

st.set_page_config(page_title="Exotic Options Lab", layout="wide")
st.title("Exotic Options & Delta Hedging Lab")
st.caption("Educational demonstration — synthetic GBM prices; discrete barrier monitoring")
a, b, c = st.columns(3)
s = a.number_input("Spot", 1.0, 10000.0, 100.0)
k = b.number_input("Strike", 1.0, 10000.0, 100.0)
sigma = c.slider("Volatility", 0.05, 1.0, 0.25, 0.01)
t = st.slider("Maturity (years)", 0.1, 2.0, 1.0, 0.1)
product = st.selectbox("Structure", ["asian", "up-and-out", "vanilla"])
barrier = st.number_input("Up-and-out barrier", value=125.0) if product == "up-and-out" else None
paths = gbm_paths(s, t, 0.0, sigma, n_paths=12000)
price, se = exotic_price(paths, k, 0, t, product, barrier=barrier)
delta = bumped_delta(paths, k, 0, t, product, barrier=barrier)
p, q, v = st.columns(3)
p.metric("Monte Carlo price", f"{price:.3f}")
q.metric("95% MC sampling interval", f"± {1.96*se:.3f}")
v.metric("Bumped delta", f"{delta:.3f}")
st.line_chart(paths[:25].T)
st.write("Black–Scholes European call benchmark:", round(black_scholes(s, k, t, 0, sigma), 3))
hedges = [hedge_short_call_path(path, k, t, 0, sigma) for path in paths[:500]]
st.write("Mean short-call discrete hedge P&L (500 synthetic paths):", round(float(np.mean(hedges)), 3))
