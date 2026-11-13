import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
from model import bs_price,implied_vol,delta_25_quotes,example_data,lagged_vol_strategy,macro_correlations

def test_implied_vol_inversion():
    p=bs_price(105,100,0.75,.02,.3)
    assert abs(implied_vol(p,105,100,0.75,.02)-.3)<1e-8

def test_rr_bf():
    q=delta_25_quotes(.2,.22,.26)
    assert q["risk_reversal_25d"]==pytest.approx(-.04)
    assert q["butterfly_25d"]==pytest.approx(.04)

def test_no_future_information_in_backtest():
    df=example_data()
    a=lagged_vol_strategy(df)
    changed=df.copy(); changed.loc[len(changed)-1,"energy_price"]*=7
    b=lagged_vol_strategy(changed)
    assert a.position.iloc[-1]==b.position.iloc[-1]
    assert a.position.between(0,1).all()

def test_rolling_correlations():
    r=macro_correlations(example_data())
    assert r.energy_vs_inflation_corr.dropna().between(-1.00001,1.00001).all()
