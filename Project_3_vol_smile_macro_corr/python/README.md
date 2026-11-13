# Volatility Smile & Macro Correlation — Python

Python companion to the original R/Quarto project: Black–Scholes implied-volatility inversion, 25-delta risk reversals/butterflies from user-supplied IV quotes, rolling energy–macro correlations, and a lagged long/cash volatility-regime backtest.

## Run

Install with `pip install -r requirements.txt`, start dashboard with `streamlit run app.py`, and test with `python -m pytest -q`.

The sample is synthetic, not FRED/OECD/exchange data. The strategy shifts exposures by one bar to avoid an obvious look-ahead error; it omits costs, financing, slippage, borrowing constraints, and parameter selection biases. Input 25-delta IV quotes must use consistent conventions. Not financial advice.

**CV:** Developed implied-volatility and 25-delta skew analytics, macro rolling correlations and a lagged volatility-regime backtest (Python).
