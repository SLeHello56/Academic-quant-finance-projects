"""Recombining trinomial tree and commodities term-structure analytics."""
import math
import pandas as pd

def trinomial_option(s, k, t, r, sigma, steps=120, kind="put", exercise="american", q=0.0, exercise_steps=None):
    """Trinomial call/put on spot with continuous carry yield q, exercise on grid."""
    if min(s,k,t,sigma) <= 0 or steps < 2:
        raise ValueError("Invalid option inputs")
    if kind not in ("call","put") or exercise not in ("european","american","bermudan"):
        raise ValueError("Unknown kind/exercise")
    dt=t/steps
    u=math.exp(sigma*math.sqrt(2*dt))
    a=math.exp((r-q)*dt/2)
    h=math.exp(sigma*math.sqrt(dt/2))
    l=1/h
    pu=((a-l)/(h-l))**2
    pd=((h-a)/(h-l))**2
    pm=1-pu-pd
    if min(pu,pm,pd) < -1e-10:
        raise ValueError("Invalid probabilities; increase steps")
    disc=math.exp(-r*dt)
    value={j:max((s*u**j-k) if kind=="call" else (k-s*u**j),0.0) for j in range(-steps,steps+1)}
    allowed=set(exercise_steps or [])
    for i in range(steps-1,-1,-1):
        next_values={}
        for j in range(-i,i+1):
            continuation=disc*(pu*value[j+1]+pm*value[j]+pd*value[j-1])
            intrinsic=max((s*u**j-k) if kind=="call" else (k-s*u**j),0.0)
            can_exercise=(exercise=="american" or (exercise=="bermudan" and i in allowed))
            next_values[j]=max(continuation,intrinsic) if can_exercise else continuation
        value=next_values
    return value[0]

def curve_metrics(curve):
    """CSV/DataFrame columns: contract, days_to_maturity, forward."""
    required={"contract","days_to_maturity","forward"}
    if not required.issubset(curve.columns):
        raise ValueError(f"Missing columns: {sorted(required-set(curve.columns))}")
    x=curve.sort_values("days_to_maturity").copy()
    if len(x)<2 or (x.forward<=0).any() or (x.days_to_maturity<=0).any():
        raise ValueError("Need at least 2 positive forwards and maturities")
    if x.days_to_maturity.duplicated().any():
        raise ValueError("Maturities must be unique")
    front,back=x.iloc[0],x.iloc[-1]
    annualized=(back.forward/front.forward-1)*365/(back.days_to_maturity-front.days_to_maturity)
    state="contango" if back.forward>front.forward else "backwardation" if back.forward<front.forward else "flat"
    x["adjacent_spread"]=x.forward.diff()
    return {"regime":state,"annualized_forward_slope":float(annualized),"front":float(front.forward),"back":float(back.forward)},x

def example_curve():
    return pd.DataFrame({"contract":["M1","M2","M3","M6","M12"],"days_to_maturity":[30,60,90,180,360],"forward":[72.0,72.8,73.6,74.9,76.2]})
