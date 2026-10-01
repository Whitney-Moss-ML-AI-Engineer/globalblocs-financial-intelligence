"""Credentialed API ingestion and analysis services for GlobalBLOCS.

Secrets are supplied at runtime and are never persisted by this module. Production
deployments should use an external secret manager or Streamlit secrets.
"""
from __future__ import annotations
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional
import pandas as pd
import requests


AUTH_METHODS = ["Bearer token", "API key header", "API key query parameter", "Basic auth", "No authentication"]

@dataclass
class APIConfig:
    provider: str
    endpoint: str
    method: str = "GET"
    auth_method: str = "Bearer token"
    credential_name: str = ""
    credential_value: str = ""
    api_key_header: str = "X-API-Key"
    api_key_param: str = "api_key"
    username: str = ""
    password: str = ""
    params: Optional[Dict[str, Any]] = None
    timeout: int = 30

    def headers(self) -> Dict[str, str]:
        h = {"Accept": "application/json", "User-Agent": "GlobalBLOCS/1.0"}
        if self.auth_method == "Bearer token" and self.credential_value:
            h["Authorization"] = f"Bearer {self.credential_value}"
        elif self.auth_method == "API key header" and self.credential_value:
            h[self.api_key_header or "X-API-Key"] = self.credential_value
        return h

    def query_params(self) -> Dict[str, Any]:
        p = dict(self.params or {})
        if self.auth_method == "API key query parameter" and self.credential_value:
            p[self.api_key_param or "api_key"] = self.credential_value
        return p


def _response_to_frame(payload: Any) -> pd.DataFrame:
    if isinstance(payload, list):
        return pd.json_normalize(payload)
    if isinstance(payload, dict):
        for key in ("data", "results", "observations", "records", "items"):
            value = payload.get(key)
            if isinstance(value, list):
                return pd.json_normalize(value)
        return pd.json_normalize(payload)
    return pd.DataFrame({"value": [payload]})


def request_api(config: APIConfig) -> Dict[str, Any]:
    auth = None
    if config.auth_method == "Basic auth" and (config.username or config.password):
        auth = (config.username, config.password)
    started = time.time()
    response = requests.request(
        config.method.upper(),
        config.endpoint,
        headers=config.headers(),
        params=config.query_params(),
        auth=auth,
        timeout=config.timeout,
    )
    elapsed = time.time() - started
    response.raise_for_status()
    content_type = response.headers.get("content-type", "")
    if "json" in content_type.lower():
        payload = response.json()
    else:
        try:
            payload = response.json()
        except ValueError:
            from io import StringIO
            return {
                "status_code": response.status_code,
                "elapsed_seconds": elapsed,
                "content_type": content_type,
                "frame": pd.read_csv(StringIO(response.text)),
                "raw": response.text,
            }
    return {
        "status_code": response.status_code,
        "elapsed_seconds": elapsed,
        "content_type": content_type,
        "frame": _response_to_frame(payload),
        "raw": payload,
    }


def normalize_ingested_data(frame: pd.DataFrame, provider: str, source_endpoint: str) -> pd.DataFrame:
    out = frame.copy()
    out.columns = [str(c).strip().lower().replace(" ", "_") for c in out.columns]
    out["source_provider"] = provider
    out["source_endpoint"] = source_endpoint
    out["retrieval_timestamp_utc"] = pd.Timestamp.utcnow().isoformat()
    out["globalblocs_ingest_layer"] = "bronze"
    return out


def analytical_summary(frame: pd.DataFrame) -> pd.DataFrame:
    numeric = frame.select_dtypes(include="number")
    if numeric.empty:
        return pd.DataFrame()
    rows = []
    for col in numeric.columns:
        s = numeric[col].dropna()
        if s.empty:
            continue
        rows.append({
            "variable": col,
            "observations": len(s),
            "latest": float(s.iloc[-1]),
            "mean": float(s.mean()),
            "std": float(s.std()) if len(s) > 1 else 0.0,
            "min": float(s.min()),
            "max": float(s.max()),
        })
    return pd.DataFrame(rows)


def trend_summary(frame: pd.DataFrame) -> pd.DataFrame:
    numeric = frame.select_dtypes(include="number")
    rows = []
    for col in numeric.columns:
        s = numeric[col].dropna()
        if len(s) < 2:
            continue
        change = float(s.iloc[-1] - s.iloc[0])
        direction = "Trending Up" if change > 0 else "Trending Down" if change < 0 else "Sideways"
        rows.append({"variable": col, "direction": direction, "change": change})
    return pd.DataFrame(rows)
