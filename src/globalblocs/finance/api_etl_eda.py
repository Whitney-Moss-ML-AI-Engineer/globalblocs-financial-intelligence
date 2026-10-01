"""ETL, EDA and feature-engineering services for credentialed GlobalBLOCS APIs."""
from __future__ import annotations
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd

def infer_data_dictionary(frame: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    for col in frame.columns:
        s=frame[col]
        nonnull=s.dropna()
        dtype=str(s.dtype)
        inferred="boolean" if pd.api.types.is_bool_dtype(s) else (
            "integer" if pd.api.types.is_integer_dtype(s) else
            "float" if pd.api.types.is_float_dtype(s) else
            "datetime" if pd.api.types.is_datetime64_any_dtype(s) else
            "numeric" if pd.api.types.is_numeric_dtype(s) else "string/object")
        unique=int(s.nunique(dropna=True))
        sample=str(nonnull.iloc[0])[:100] if len(nonnull) else ""
        rows.append({"variable":str(col),"pandas_dtype":dtype,"inferred_type":inferred,
                     "rows":len(s),"non_null":int(s.notna().sum()),
                     "missing_pct":round(float(s.isna().mean()*100),3),
                     "unique_values":unique,"sample_value":sample})
    return pd.DataFrame(rows)

def profile_eda(frame: pd.DataFrame) -> Dict[str, Any]:
    numeric=frame.select_dtypes(include="number")
    categorical=frame.select_dtypes(exclude="number")
    return {
        "rows":len(frame),"columns":len(frame.columns),
        "numeric_columns":len(numeric.columns),"categorical_columns":len(categorical.columns),
        "duplicate_rows":int(frame.duplicated().sum()),
        "missing_cells":int(frame.isna().sum().sum()),
        "constant_columns":[c for c in frame.columns if frame[c].nunique(dropna=False)<=1],
        "high_missing_columns":[c for c in frame.columns if frame[c].isna().mean()>=0.5],
        "numeric_summary":numeric.describe().T.reset_index().rename(columns={"index":"variable"}).to_dict("records") if not numeric.empty else [],
    }

def apply_transformations(frame: pd.DataFrame, rules: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    out=frame.copy(); audit=[]
    for rule in rules:
        col=rule.get("column"); op=rule.get("operation")
        if col not in out.columns: audit.append({**rule,"status":"SKIPPED","reason":"column not found"}); continue
        before=str(out[col].dtype)
        try:
            if op=="to_numeric": out[col]=pd.to_numeric(out[col],errors="coerce")
            elif op=="to_datetime": out[col]=pd.to_datetime(out[col],errors="coerce",utc=True)
            elif op=="percent_to_decimal": out[col]=pd.to_numeric(out[col],errors="coerce")/100.0
            elif op=="decimal_to_percent": out[col]=pd.to_numeric(out[col],errors="coerce")*100.0
            elif op=="thousands_to_units": out[col]=pd.to_numeric(out[col],errors="coerce")*1000.0
            elif op=="millions_to_units": out[col]=pd.to_numeric(out[col],errors="coerce")*1_000_000.0
            elif op=="billions_to_units": out[col]=pd.to_numeric(out[col],errors="coerce")*1_000_000_000.0
            elif op=="strip_percent_sign": out[col]=pd.to_numeric(out[col].astype(str).str.replace("%","",regex=False),errors="coerce")
            elif op=="lowercase": out[col]=out[col].astype(str).str.lower()
            elif op=="rename": out=out.rename(columns={col:rule.get("new_name",col)})
            else: audit.append({**rule,"status":"SKIPPED","reason":"unsupported operation"}); continue
            audit.append({**rule,"status":"APPLIED","dtype_before":before,"dtype_after":str(out[col if op!="rename" else rule.get("new_name",col)].dtype)})
        except Exception as exc: audit.append({**rule,"status":"FAILED","reason":str(exc)})
    return out,pd.DataFrame(audit)

def build_feature_table(frame: pd.DataFrame, feature_rules: List[Dict[str, Any]]) -> Tuple[pd.DataFrame,pd.DataFrame]:
    out=pd.DataFrame(index=frame.index); audit=[]
    for rule in feature_rules:
        name=rule.get("feature_name"); source=rule.get("source_column"); op=rule.get("operation")
        if source not in frame.columns: audit.append({**rule,"status":"SKIPPED","reason":"source missing"}); continue
        s=pd.to_numeric(frame[source],errors="coerce")
        try:
            if op=="raw": f=s
            elif op=="pct_change": f=s.pct_change()
            elif op=="diff": f=s.diff()
            elif op=="rolling_mean": f=s.rolling(int(rule.get("window",20))).mean()
            elif op=="rolling_std": f=s.rolling(int(rule.get("window",20))).std()
            elif op=="zscore": f=(s-s.mean())/s.std()
            elif op=="log1p": f=np.log1p(s.clip(lower=0))
            elif op=="lag": f=s.shift(int(rule.get("periods",1)))
            else: audit.append({**rule,"status":"SKIPPED","reason":"unsupported feature operation"}); continue
            out[name]=f; audit.append({**rule,"status":"APPLIED","feature_dtype":str(f.dtype)})
        except Exception as exc: audit.append({**rule,"status":"FAILED","reason":str(exc)})
    return out,pd.DataFrame(audit)

def feature_matrix(feature_table: pd.DataFrame) -> pd.DataFrame:
    return feature_table.select_dtypes(include=[np.number]).copy()

def api_etl_eda_pipeline(frame: pd.DataFrame, provider: str, endpoint: str,
                         transform_rules: List[Dict[str,Any]]|None=None,
                         feature_rules: List[Dict[str,Any]]|None=None) -> Dict[str,Any]:
    raw=frame.copy()
    dictionary=infer_data_dictionary(raw)
    eda_before=profile_eda(raw)
    transformed,audit=apply_transformations(raw,transform_rules or [])
    feature_tbl,feature_audit=build_feature_table(transformed,feature_rules or [])
    matrix=feature_matrix(feature_tbl)
    transformed["globalblocs_layer"]="silver"
    return {"raw":raw,"data_dictionary":dictionary,"eda_before":eda_before,
            "silver":transformed,"transformation_audit":audit,
            "feature_table":feature_tbl,"feature_audit":feature_audit,
            "feature_matrix":matrix,
            "provenance":{"provider":provider,"endpoint":endpoint,
                          "retrieval_timestamp_utc":pd.Timestamp.utcnow().isoformat(),
                          "pipeline":"API → Bronze → EDA → Transform → Silver → Feature Table → Feature Matrix"}}
