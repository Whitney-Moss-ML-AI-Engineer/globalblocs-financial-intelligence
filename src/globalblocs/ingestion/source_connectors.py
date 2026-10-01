"""Production source connector registry and HTTP ingestion helpers.

Connectors describe official/public or credentialed sources without embedding
secrets. Provider-specific authentication belongs in the runtime API layer.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import pandas as pd
import requests

@dataclass(frozen=True)
class SourceSpec:
    id: str
    provider: str
    domain: str
    description: str
    url: str
    auth: str = "none"
    format: str = "json"

SOURCE_REGISTRY = [
    SourceSpec("fred", "Federal Reserve FRED", "macro", "Macroeconomic time series", "https://api.stlouisfed.org/fred/series/observations", "api_key"),
    SourceSpec("sec-edgar", "U.S. SEC EDGAR", "corporate", "Company filings and submissions", "https://data.sec.gov/submissions/", "user_agent"),
    SourceSpec("fdic", "FDIC", "banking", "Bank and deposit institution data", "https://banks.data.fdic.gov/api/", "none"),
    SourceSpec("world-bank", "World Bank", "global", "Cross-country development indicators", "https://api.worldbank.org/v2/", "none"),
    SourceSpec("cftc", "CFTC", "derivatives", "Commitment of Traders datasets", "https://publicreporting.cftc.gov/", "none"),
    SourceSpec("finra", "FINRA", "markets", "Broker/dealer and market datasets", "https://api.finra.org/", "credentialed"),
    SourceSpec("cfpb", "CFPB", "consumer", "Consumer complaint datasets", "https://www.consumerfinance.gov/data-research/consumer-complaints/", "none"),
    SourceSpec("custom", "Credentialed API", "custom", "Runtime-configured external API", "", "runtime"),
]

def list_sources() -> list[dict[str, Any]]:
    return [s.__dict__ for s in SOURCE_REGISTRY]

def get_source(source_id: str) -> SourceSpec:
    for source in SOURCE_REGISTRY:
        if source.id == source_id:
            return source
    raise KeyError(source_id)

def fetch_json(url: str, *, params: dict[str, Any] | None = None,
               headers: dict[str, str] | None = None, timeout: int = 30) -> Any:
    response = requests.get(url, params=params or {}, headers=headers or {}, timeout=timeout)
    response.raise_for_status()
    return response.json()

def json_records(payload: Any) -> pd.DataFrame:
    if isinstance(payload, list):
        return pd.json_normalize(payload)
    if isinstance(payload, dict):
        for key in ("data", "results", "observations", "records", "items"):
            if isinstance(payload.get(key), list):
                return pd.json_normalize(payload[key])
        return pd.json_normalize(payload)
    return pd.DataFrame({"value": [payload]})
