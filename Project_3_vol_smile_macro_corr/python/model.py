"""Implied volatility, 25-delta quotes and lagged macro/volatility strategy."""
from math import erf,exp,log,sqrt
import numpy as np
import pandas as pd

def cdf(x):
    return (1+erf(x/sqrt(2)))/2

def bs_price(s,k,t,r,vol,kind="call"):
    if min(s,k,t,vol)<=0:
        raise ValueError("Positive spot/strike/maturity/volatility required")
    d1=(log(s/k)+(r+vol**2/2)*t)/(vol*sqrt(t))
    d2=d1-vol*sqrt(t)
    c=s*cdf(d1)-k*exp(-r*t)*cdf(d2)
    if kind=="call": return c
    if kind=="put": return c-s+k*exp(-r*t)
    raise ValueError("Unknown option kind")

def implied_vol(price,s,k,t,r,kind="call",low=0.00001,high=5.0):
    if kind not in ("call","put"):
        raise ValueError("Unknown option kind")
    if price<=0 or price<bs_price(s,k,t,r,low,kind)-1e-8 or price>bs_price(s,k,t,r,high,kind)+1e-8:
        raise ValueError("Option price outside Black–Scholes range")
    for _ in range(90):
        m=(low+high)/2
        if bs_price(s,k,t,r,m,kind)<price: low=m
        else: high=m
    return (low+high)/2

def delta_25_quotes(atm,call25,put25):
    """IV in decimal units for matched +25delta call / -25delta put."""
    if min(atm,call25,put25)<=0:
        raise ValueError("Volatilities must be positive")
    return {"risk_reversal_25d":call25-put25,"butterfly_25d":(call25+put25)/2-atm}

def macro_correlations(df,window=30):
    """Trailing correlations between log energy returns and macro first differences."""
    d=df.sort_values("date").copy()
    if (d["energy_price"]<=0).any():
        raise ValueError("Energy price must be positive")
    e=np.log(d["energy_price"]).diff()
    d["energy_vs_inflation_corr"]=e.rolling(window).corr(d["inflation_yoy"].diff())
    d["energy_vs_rates_corr"]=e.rolling(window).corr(d["rate_10y"].diff())
    return d

def lagged_vol_strategy(df,window=20):
    """Long energy only in low realized-vol regime; one-bar lag."""
    d=df.sort_values("date").copy()
    ret=d.energy_price.pct_change()
    realized=ret.rolling(window,min_periods=window).std()
    trailing_median=realized.rolling(window*3,min_periods=window).median()
    signal=(realized<trailing_median).astype(float).where(trailing_median.notna())
    d["position"]=signal.shift(1).fillna(0.0)
    d["asset_return"]=ret.fillna(0.0)
    d["strategy_return"]=d.position*d.asset_return
    d["strategy_equity"]=(1+d.strategy_return).cumprod()
    d["buy_hold_equity"]=(1+d.asset_return).cumprod()
    return d

def example_data(n=300,seed=37):
    rng=np.random.default_rng(seed)
    shock=rng.standard_normal(n)
    energy=75*np.exp(np.cumsum(0.00015+0.018*shock))
    return pd.DataFrame({"date":pd.date_range("2025-01-02",periods=n,freq="B"),"energy_price":energy,
                         "inflation_yoy":2.3+np.cumsum(rng.normal(0,0.025,n)),
                         "rate_10y":3.4+np.cumsum(rng.normal(0,0.018,n))})
