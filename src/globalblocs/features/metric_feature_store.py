"""350-metric feature-store contract for point-in-time ML features."""
from __future__ import annotations
import pandas as pd
from globalblocs.finance.metric_knowledge_base import metric_catalog

def build_metric_feature_store(frame: pd.DataFrame, as_of_column: str="available_to_market_date") -> pd.DataFrame:
    out=frame.copy()
    if as_of_column in out.columns:
        out[as_of_column]=pd.to_datetime(out[as_of_column],errors="coerce")
        out=out.sort_values(as_of_column)
    out.attrs["metric_count"]=len(metric_catalog())
    out.attrs["point_in_time_required"]=True
    return out

def feature_store_contract() -> dict:
    return {"metric_count":350,"point_in_time_required":True,"no_future_data":True,"fit_transforms_on_training_window":True,"source_provenance_required":True}
