# Exotic Options Lab — Python

Path-dependent options pricing and discrete hedging. Black–Scholes benchmark, antithetic Monte Carlo Asian fixed-strike and discretely monitored up-and-out options, finite-difference deltas with common random numbers, short vanilla call delta-hedging P&L.

## Run

Install with `pip install -r requirements.txt`, start dashboard with `streamlit run app.py`, and test with `python -m pytest -q`.

**Methodology:** synthetic GBM simulations with a reproducible seed. 95% Monte Carlo confidence intervals reflect sampling error only, not model error. Up-and-out monitoring is discrete; no continuous-barrier correction. Hedge is for a **vanilla** short call at r=0 and omits fees, spreads, funding and slippage. Not an investable strategy or advice.

**CV:** Developed Monte Carlo pricers for Asian/barrier options, numerical Greeks and discrete delta-hedging analysis (Python).
