"""Reusable data-quality and provenance gates for GlobalBLOCS."""
from __future__ import annotations
from typing import Any
import pandas as pd

def profile(frame: pd.DataFrame) -> dict[str, Any]:
    missing = frame.isna().sum()
    return {
        "rows": int(len(frame)),
        "columns": int(len(frame.columns)),
        "duplicate_rows": int(frame.duplicated().sum()),
        "missing_cells": int(frame.isna().sum().sum()),
        "constant_columns": [c for c in frame.columns if frame[c].nunique(dropna=False) <= 1],
        "high_missing_columns": [c for c in frame.columns if frame[c].isna().mean() >= 0.50],
        "numeric_columns": frame.select_dtypes(include="number").columns.tolist(),
        "categorical_columns": frame.select_dtypes(exclude="number").columns.tolist(),
        "missing_pct": {str(c): round(float(v / max(len(frame), 1) * 100), 2) for c, v in missing.items()},
    }

def quality_score(frame: pd.DataFrame) -> float:
    if frame.empty:
        return 0.0
    missing_penalty = float(frame.isna().mean().mean())
    duplicate_penalty = float(frame.duplicated().mean())
    return round(max(0.0, 100.0 * (1 - missing_penalty - duplicate_penalty)), 2)

def provenance(frame: pd.DataFrame, *, provider: str, endpoint: str,
               retrieval_timestamp_utc: str | None = None) -> pd.DataFrame:
    out = frame.copy()
    out["source_provider"] = provider
    out["source_endpoint"] = endpoint
    out["retrieval_timestamp_utc"] = retrieval_timestamp_utc or pd.Timestamp.now(tz="UTC").isoformat()
    out["data_quality_score"] = quality_score(frame)
    return out
