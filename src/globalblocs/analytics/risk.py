"""Portfolio and market-risk analytics used by the production API."""
from __future__ import annotations
import numpy as np
import pandas as pd

def returns(prices: pd.Series) -> pd.Series:
    return pd.to_numeric(prices, errors="coerce").pct_change().dropna()

def volatility(prices: pd.Series, periods_per_year: int = 252) -> float:
    r = returns(prices)
    return float(r.std() * np.sqrt(periods_per_year)) if len(r) > 1 else float("nan")

def maximum_drawdown(prices: pd.Series) -> float:
    p = pd.to_numeric(prices, errors="coerce").dropna()
    if p.empty:
        return float("nan")
    drawdown = p / p.cummax() - 1.0
    return float(drawdown.min())

def sharpe_ratio(prices: pd.Series, risk_free: float = 0.0,
                 periods_per_year: int = 252) -> float:
    r = returns(prices)
    if len(r) < 2 or r.std() == 0:
        return float("nan")
    return float((r.mean() * periods_per_year - risk_free) /
                 (r.std() * np.sqrt(periods_per_year)))

def var_historical(prices: pd.Series, confidence: float = 0.95) -> float:
    r = returns(prices)
    return float(r.quantile(1 - confidence)) if not r.empty else float("nan")

def cvar_historical(prices: pd.Series, confidence: float = 0.95) -> float:
    r = returns(prices)
    if r.empty:
        return float("nan")
    cutoff = r.quantile(1 - confidence)
    tail = r[r <= cutoff]
    return float(tail.mean()) if not tail.empty else float(cutoff)

def risk_summary(prices: pd.Series) -> dict[str, float]:
    return {
        "volatility": volatility(prices),
        "maximum_drawdown": maximum_drawdown(prices),
        "sharpe_ratio": sharpe_ratio(prices),
        "historical_var_95": var_historical(prices),
        "historical_cvar_95": cvar_historical(prices),
    }
