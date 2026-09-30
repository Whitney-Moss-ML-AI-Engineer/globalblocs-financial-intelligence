"""HTTP ingestion helpers with source lineage preservation."""
from __future__ import annotations
from datetime import datetime, timezone
from io import BytesIO
import pandas as pd
import requests

def fetch_json(url, params=None, headers=None):
    r = requests.get(url, params=params, headers=headers, timeout=60)
    r.raise_for_status()
    return r.json()

def fetch_csv(url, **kwargs):
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    return pd.read_csv(BytesIO(r.content), **kwargs)

def fetch_excel(url, **kwargs):
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    return pd.read_excel(BytesIO(r.content), **kwargs)

def add_lineage(df, source_id, dataset_id, source_url):
    out = df.copy()
    out["source_id"] = source_id
    out["dataset_id"] = dataset_id
    out["source_url"] = source_url
    out["retrieved_at_utc"] = datetime.now(timezone.utc).isoformat()
    return out
