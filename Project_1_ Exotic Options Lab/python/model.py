"""Teaching models for exotic options. Discrete barrier monitoring, no transaction costs."""
from math import erf, exp, log, sqrt
import numpy as np

def norm_cdf(x):
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))

def black_scholes(s, k, t, r, sigma, kind="call"):
    if min(s, k) <= 0 or t <= 0 or sigma <= 0:
        raise ValueError("S, K, T and sigma must be positive")
    d1 = (log(s / k) + (r + sigma * sigma / 2) * t) / (sigma * sqrt(t))
    d2 = d1 - sigma * sqrt(t)
    call = s * norm_cdf(d1) - k * exp(-r * t) * norm_cdf(d2)
    if kind not in ("call", "put"):
        raise ValueError("kind must be call or put")
    return call if kind == "call" else call - s + k * exp(-r * t)

def bs_call_delta(s, k, t, r, sigma):
    if t <= 0:
        return float(s > k)
    d1 = (log(s / k) + (r + 0.5 * sigma**2) * t) / (sigma * sqrt(t))
    return norm_cdf(d1)

def gbm_paths(s, t, r, sigma, steps=52, n_paths=20000, seed=7):
    """Antithetic risk-neutral GBM paths, including initial spot."""
    if steps < 1 or n_paths < 2 or s <= 0 or t <= 0 or sigma <= 0:
        raise ValueError("Invalid GBM inputs")
    rng = np.random.default_rng(seed)
    half = (n_paths + 1) // 2
    z = rng.standard_normal((half, steps))
    z = np.concatenate([z, -z], axis=0)[:n_paths]
    dt = t / steps
    growth = (r - 0.5 * sigma**2) * dt + sigma * sqrt(dt) * z
    paths = np.concatenate([np.ones((n_paths, 1)), np.exp(np.cumsum(growth, axis=1))], axis=1)
    return s * paths

def exotic_price(paths, k, r, t, product="asian", option_type="call", barrier=None):
    """Discounted payoff. Asian average excludes t=0."""
    if product not in {"asian", "up-and-out", "vanilla"}:
        raise ValueError("Unsupported product")
    if option_type not in {"call", "put"}:
        raise ValueError("Unsupported option type")
    reference = paths[:, 1:].mean(axis=1) if product == "asian" else paths[:, -1]
    payoff = np.maximum(reference - k, 0) if option_type == "call" else np.maximum(k - reference, 0)
    if product == "up-and-out":
        if barrier is None or barrier <= 0:
            raise ValueError("Positive barrier required")
        payoff = payoff * (paths.max(axis=1) < barrier)
    discounted = np.exp(-r * t) * payoff
    return float(discounted.mean()), float(discounted.std(ddof=1) / sqrt(len(discounted)))

def bumped_delta(paths, k, r, t, product="asian", barrier=None, bump=0.01):
    """Finite-difference delta with common random numbers."""
    if bump <= 0 or bump >= 1:
        raise ValueError("Bump must be between 0 and 1")
    up = exotic_price(paths * (1 + bump), k, r, t, product, barrier=barrier)[0]
    down = exotic_price(paths * (1 - bump), k, r, t, product, barrier=barrier)[0]
    return (up - down) / (2 * bump * paths[0, 0])

def hedge_short_call_path(path, k, t, r, sigma):
    """Discrete short vanilla call delta hedge, zero financing rate."""
    if r != 0:
        raise ValueError("Hedge illustration only supports r=0")
    steps = len(path) - 1
    if steps <= 0:
        raise ValueError("Need at least one hedge step")
    delta = bs_call_delta(path[0], k, t, r, sigma)
    cash = black_scholes(path[0], k, t, r, sigma) - delta * path[0]
    for i in range(1, steps):
        new_delta = bs_call_delta(path[i], k, t * (1 - i / steps), r, sigma)
        cash -= (new_delta - delta) * path[i]
        delta = new_delta
    payoff = max(path[-1] - k, 0)
    return float(cash + delta * path[-1] - payoff)
