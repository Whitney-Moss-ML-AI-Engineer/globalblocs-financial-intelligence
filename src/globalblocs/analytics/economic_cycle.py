"""Business-cycle classification and descriptive macro screening."""
from __future__ import annotations
from typing import Any
import pandas as pd

def slope(values: pd.Series) -> float:
    y = pd.to_numeric(values, errors="coerce").dropna()
    if len(y) < 2:
        return float("nan")
    x = pd.Series(range(len(y)), index=y.index)
    return float(((x - x.mean()) * (y - y.mean())).sum() / ((x - x.mean()) ** 2).sum())

def classify_business_cycle(*, gdp_growth: float | None = None,
                            unemployment_slope: float | None = None,
                            industrial_production_slope: float | None = None,
                            yield_curve_spread: float | None = None) -> str:
    if gdp_growth is None:
        return "Insufficient Data"
    weakening = (unemployment_slope is not None and unemployment_slope > 0) and (
        industrial_production_slope is None or industrial_production_slope < 0)
    improving = (unemployment_slope is not None and unemployment_slope < 0) and (
        industrial_production_slope is None or industrial_production_slope > 0)
    if gdp_growth < 0 and weakening:
        return "Contraction"
    if gdp_growth > 0 and improving:
        return "Expansion"
    if yield_curve_spread is not None and yield_curve_spread < 0 and gdp_growth > 0:
        return "Late Cycle / Transition"
    return "Transition"

def business_cycle_screen(frame: pd.DataFrame, gdp_col: str = "gdp_growth",
                          unemployment_col: str = "unemployment",
                          industrial_col: str = "industrial_production",
                          spread_col: str = "yield_curve_spread") -> dict[str, Any]:
    latest = frame.iloc[-1] if not frame.empty else {}
    return {
        "phase": classify_business_cycle(
            gdp_growth=float(latest[gdp_col]) if gdp_col in frame and pd.notna(latest[gdp_col]) else None,
            unemployment_slope=slope(frame[unemployment_col]) if unemployment_col in frame else None,
            industrial_production_slope=slope(frame[industrial_col]) if industrial_col in frame else None,
            yield_curve_spread=float(latest[spread_col]) if spread_col in frame and pd.notna(latest[spread_col]) else None,
        ),
        "observations": int(len(frame)),
    }
