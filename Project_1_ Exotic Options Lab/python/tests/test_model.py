import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from math import exp
from model import black_scholes, gbm_paths, exotic_price, bumped_delta, hedge_short_call_path

def test_put_call_parity():
    s,k,t,r,v = 102,100,0.5,0.04,0.2
    assert abs(black_scholes(s,k,t,r,v)-black_scholes(s,k,t,r,v,"put")-(s-k*exp(-r*t))) < 1e-9

def test_mc_european_close_to_bs():
    paths = gbm_paths(100,1,0,0.2,n_paths=50000)
    price,se = exotic_price(paths,100,0,1,"vanilla")
    assert abs(price-black_scholes(100,100,1,0,0.2)) < 4*se

def test_barrier_never_more_than_vanilla():
    paths = gbm_paths(100,1,0,0.2)
    vanilla,_ = exotic_price(paths,100,0,1,"vanilla")
    knockout,_ = exotic_price(paths,100,0,1,"up-and-out",barrier=125)
    assert 0 <= knockout <= vanilla

def test_delta_and_hedge_finite():
    paths = gbm_paths(100,1,0,0.2,n_paths=1000)
    assert 0 < bumped_delta(paths,100,0,1) < 1.1
    assert abs(hedge_short_call_path(paths[0],100,1,0,0.2)) < 100
