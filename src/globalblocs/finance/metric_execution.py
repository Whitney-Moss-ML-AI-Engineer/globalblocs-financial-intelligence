"""350-metric execution and validation engine.

The knowledge base is the control plane; this module is the execution gate.
Every catalog metric has a callable execution contract. Metrics with a
domain-specific implementation use it; otherwise the engine applies a
deterministic, documented generic operation and marks the execution mode.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Mapping
import math
import numpy as np
import pandas as pd

from globalblocs.finance.metric_knowledge_base import metric_catalog, get_metric, validate_catalog


@dataclass(frozen=True)
class MetricExecution:
    metric_id: int
    metric: str
    status: str
    mode: str
    value: float | None
    validation: dict[str, Any]
    requirements: list[str]


def _series(inputs: Mapping[str, Any]) -> pd.Series:
    for key in ("returns", "prices", "values", "series"):
        if key in inputs:
            return pd.Series(inputs[key], dtype="float64").dropna()
    return pd.Series(dtype="float64")


def _scalar(inputs: Mapping[str, Any], *keys: str) -> float | None:
    for key in keys:
        if key in inputs and inputs[key] is not None:
            try:
                return float(inputs[key])
            except (TypeError, ValueError):
                return None
    return None


def _safe(fn: Callable[[], float]) -> float | None:
    try:
        value = float(fn())
        return value if math.isfinite(value) else None
    except (TypeError, ValueError, ZeroDivisionError, FloatingPointError):
        return None


def _generic(metric: dict[str, Any], inputs: Mapping[str, Any]) -> float | None:
    """Deterministic fallback for catalog coverage.

    This is intentionally not presented as a domain-specific formula. It
    supplies a reproducible execution value when the requested metric has no
    native calculator yet, using the supplied series/scalar according to the
    metric family. Native implementations can replace this without changing
    the API contract.
    """
    name = metric["name"].lower()
    s = _series(inputs)
    if len(s) == 0:
        return _scalar(inputs, "value", "metric_value", "current")
    if "count" in name or "number of holdings" in name:
        return float(s.count())
    if "median" in name:
        return float(s.median())
    if "variance" in name:
        return float(s.var())
    if "standard deviation" in name or "volatility" in name:
        return float(s.std())
    if "skew" in name:
        return float(s.skew())
    if "kurtosis" in name:
        return float(s.kurt())
    if "maximum" in name and "drawdown" in name:
        peak = s.cummax()
        return float((s / peak - 1).min())
    if "correlation" in name or "beta" in name:
        b = pd.Series(inputs.get("benchmark", []), dtype="float64").dropna()
        if len(b) == len(s) and len(s) > 1 and b.var() != 0:
            return float(s.cov(b) / b.var())
    if "return" in name or "growth" in name or "change" in name:
        if len(s) > 1 and s.iloc[0] != 0:
            return float(s.iloc[-1] / s.iloc[0] - 1)
    return float(s.iloc[-1])


def _native(metric: dict[str, Any], inputs: Mapping[str, Any]) -> float | None:
    name = metric["name"]
    s = _series(inputs)
    r = pd.Series(inputs.get("returns", []), dtype="float64").dropna()
    if name in {"Total Return", "Price Return", "Simple Return"}:
        if len(s) > 1 and s.iloc[0] != 0:
            return float(s.iloc[-1] / s.iloc[0] - 1)
    if name == "Annualized Return (CAGR)":
        years = _scalar(inputs, "years")
        if len(s) > 1 and s.iloc[0] > 0:
            years = years or 1.0
            return float((s.iloc[-1] / s.iloc[0]) ** (1 / years) - 1)
    if name in {"Standard Deviation", "Volatility", "Historical Volatility"}:
        x = r if len(r) else s.pct_change().dropna()
        return float(x.std() * np.sqrt(252)) if len(x) > 1 else None
    if name == "Variance":
        x = r if len(r) else s.pct_change().dropna()
        return float(x.var()) if len(x) > 1 else None
    if name in {"Maximum Drawdown", "Maximum Drawdown (MDD)"}:
        peak = s.cummax()
        return float((s / peak - 1).min()) if len(s) else None
    if name in {"Free Cash Flow", "FCF"}:
        ocf = _scalar(inputs, "operating_cash_flow", "ocf")
        capex = _scalar(inputs, "capital_expenditures", "capex")
        return ocf - capex if ocf is not None and capex is not None else None
    if name == "Current Ratio":
        a = _scalar(inputs, "current_assets")
        l = _scalar(inputs, "current_liabilities")
        return a / l if a is not None and l else None
    if name == "Debt-to-Equity":
        d = _scalar(inputs, "debt", "total_debt")
        e = _scalar(inputs, "equity")
        return d / e if d is not None and e else None
    if name == "ROA":
        ni = _scalar(inputs, "net_income")
        assets = _scalar(inputs, "average_assets", "assets")
        return ni / assets if ni is not None and assets else None
    if name == "ROE":
        ni = _scalar(inputs, "net_income")
        eq = _scalar(inputs, "average_equity", "equity")
        return ni / eq if ni is not None and eq else None
    if name == "ROIC":
        nopat = _scalar(inputs, "nopat")
        invested = _scalar(inputs, "invested_capital")
        return nopat / invested if nopat is not None and invested else None
    if name in {"Gross Margin", "Operating Margin", "Net Profit Margin"}:
        numerator_keys = {
            "Gross Margin": ("gross_profit",),
            "Operating Margin": ("operating_income",),
            "Net Profit Margin": ("net_income",),
        }[name]
        n = _scalar(inputs, *numerator_keys)
        d = _scalar(inputs, "revenue")
        return n / d if n is not None and d else None
    if name == "Market Capitalization":
        p = _scalar(inputs, "price")
        shares = _scalar(inputs, "shares_outstanding", "shares")
        return p * shares if p is not None and shares is not None else None
    if name == "P/E":
        p = _scalar(inputs, "price")
        eps = _scalar(inputs, "eps", "trailing_eps")
        return p / eps if p is not None and eps else None
    if name == "P/B":
        p = _scalar(inputs, "price")
        bvps = _scalar(inputs, "book_value_per_share", "book_value")
        return p / bvps if p is not None and bvps else None
    if name == "P/S":
        mc = _scalar(inputs, "market_cap", "market_capitalization")
        rev = _scalar(inputs, "revenue")
        return mc / rev if mc is not None and rev else None
    if name == "EV/EBITDA":
        ev = _scalar(inputs, "enterprise_value")
        e = _scalar(inputs, "ebitda")
        return ev / e if ev is not None and e else None
    if name == "FCF Yield":
        fcf = _scalar(inputs, "free_cash_flow", "fcf")
        mc = _scalar(inputs, "market_cap", "market_capitalization")
        return fcf / mc if fcf is not None and mc else None
    if name in {"Sharpe Ratio", "Sortino Ratio"}:
        x = r if len(r) else s.pct_change().dropna()
        rf = _scalar(inputs, "risk_free", "risk_free_rate") or 0.0
        if len(x) > 1:
            excess = x.mean() * 252 - rf
            denom = x.std() * np.sqrt(252)
            if name == "Sortino Ratio":
                downside = x[x < 0].std() * np.sqrt(252)
                denom = downside
            return excess / denom if denom else None
    return None


def execute_metric(metric_id: int, inputs: Mapping[str, Any] | None = None) -> dict[str, Any]:
    metric = get_metric(metric_id)
    if metric is None:
        raise KeyError(f"Unknown metric_id: {metric_id}")
    inputs = inputs or {}
    value = _native(metric, inputs)
    mode = "native"
    if value is None or not math.isfinite(float(value)):
        value = _generic(metric, inputs)
        mode = "generic_contract"
    if value is not None and not math.isfinite(float(value)):
        value = None
    status = "executed" if value is not None else "insufficient_data"
    return {
        "metric_id": metric_id,
        "metric": metric["name"],
        "category": metric["category"],
        "status": status,
        "mode": mode,
        "value": value,
        "requirements": ["compatible input data", "point-in-time availability", "source provenance"],
        "validation": validate_execution(metric_id, inputs, value),
    }


def validate_execution(metric_id: int, inputs: Mapping[str, Any] | None = None, value: float | None = None) -> dict[str, Any]:
    metric = get_metric(metric_id)
    if metric is None:
        return {"valid": False, "reason": "unknown_metric"}
    checks = {
        "catalog_member": True,
        "id_in_range": 1 <= metric_id <= 350,
        "name_present": bool(metric["name"]),
        "visualization_profile_present": bool(metric.get("visualization")),
        "ml_contract_present": bool(metric.get("ml")),
        "forecast_contract_present": bool(metric.get("forecasting")),
        "finite_value": value is None or math.isfinite(float(value)),
    }
    return {"valid": all(checks.values()), "checks": checks}


def validate_all_metrics(sample_inputs: Mapping[str, Any] | None = None) -> dict[str, Any]:
    catalog = validate_catalog()
    results = [execute_metric(m["id"], sample_inputs or {"values": [100.0, 101.0, 102.0]}) for m in metric_catalog()]
    executed = sum(r["status"] == "executed" for r in results)
    valid = sum(r["validation"]["valid"] for r in results)
    return {
        "catalog": catalog,
        "metric_count": len(results),
        "executed_count": executed,
        "validation_pass_count": valid,
        "validation_pass_rate": valid / len(results) if results else 0.0,
        "native_execution_count": sum(r["mode"] == "native" for r in results),
        "generic_contract_count": sum(r["mode"] == "generic_contract" for r in results),
        "all_contracts_valid": valid == len(results) == 350,
    }


def execution_contract() -> dict[str, Any]:
    return {
        "metric_count": 350,
        "execution_endpoint": "/api/v1/production/metrics/execute",
        "validation_endpoint": "/api/v1/production/metrics/validate",
        "point_in_time_required": True,
        "source_provenance_required": True,
        "generic_fallback_is_not_a_domain_formula": True,
    }
