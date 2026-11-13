import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
from model import trinomial_option,curve_metrics,example_curve

def test_american_put_ge_european():
    eu=trinomial_option(95,100,1,.03,.25,kind="put",exercise="european")
    am=trinomial_option(95,100,1,.03,.25,kind="put",exercise="american")
    assert am>=eu-1e-10

def test_bermudan_between_european_and_american():
    args=(95,100,1,.03,.25)
    eu=trinomial_option(*args,exercise="european")
    bm=trinomial_option(*args,exercise="bermudan",exercise_steps=[30,60,90])
    am=trinomial_option(*args,exercise="american")
    assert eu-1e-8<=bm<=am+1e-8

def test_curve_regime():
    metrics,_=curve_metrics(example_curve())
    assert metrics["regime"]=="contango"
    d=example_curve(); d["forward"]=list(reversed(d["forward"].tolist()))
    assert curve_metrics(d)[0]["regime"]=="backwardation"

def test_invalid_duplicate_maturities():
    d=example_curve(); d.loc[1,"days_to_maturity"]=30
    with pytest.raises(ValueError): curve_metrics(d)
