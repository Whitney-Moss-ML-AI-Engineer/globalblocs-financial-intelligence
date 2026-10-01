"""Financial, macroeconomic and time-series feature engineering primitives."""
from __future__ import annotations
import numpy as np
import pandas as pd

def add_time_features(frame: pd.DataFrame, date_column: str) -> pd.DataFrame:
    out = frame.copy()
    dt = pd.to_datetime(out[date_column], errors="coerce")
    out["year"] = dt.dt.year
    out["quarter"] = dt.dt.quarter
    out["month"] = dt.dt.month
    out["week"] = dt.dt.isocalendar().week.astype("Int64")
    return out

def add_series_features(frame: pd.DataFrame, column: str, windows=(5, 21, 63)) -> pd.DataFrame:
    out = frame.copy()
    s = pd.to_numeric(out[column], errors="coerce")
    out[f"{column}_diff"] = s.diff()
    out[f"{column}_pct_change"] = s.pct_change()
    for window in windows:
        out[f"{column}_ma_{window}"] = s.rolling(window).mean()
        out[f"{column}_vol_{window}"] = s.pct_change().rolling(window).std()
        out[f"{column}_z_{window}"] = (s - s.rolling(window).mean()) / s.rolling(window).std()
    return out

def add_lags(frame: pd.DataFrame, column: str, lags=(1, 5, 21, 63)) -> pd.DataFrame:
    out = frame.copy()
    for lag in lags:
        out[f"{column}_lag_{lag}"] = pd.to_numeric(out[column], errors="coerce").shift(lag)
    return out

def build_features(frame: pd.DataFrame, value_columns: list[str]) -> pd.DataFrame:
    out = frame.copy()
    for column in value_columns:
        if column in out:
            out = add_series_features(out, column)
            out = add_lags(out, column)
    return out.replace([np.inf, -np.inf], np.nan)
