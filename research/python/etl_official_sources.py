"""Small, auditable ETL starter for World Bank WDI and FRED.

Examples:
  python research/python/etl_official_sources.py --start 2000 --end 2024
Environment:
  FRED_API_KEY (optional; required for FRED API calls)

Raw responses/normalized tables are written under data/raw and data/processed.
IMF and BIS are intentionally not hard-coded to a guessed universal series key:
their SDMX dataflows/dimensions must be discovered and configured for the selected dataset.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
USER_AGENT = "GlobalBLOCSResearch/0.1 (research data pipeline)"


def get_json(url: str, params: dict[str, Any] | None = None) -> Any:
    response = requests.get(
        url, params=params, timeout=45,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    response.raise_for_status()
    time.sleep(0.15)
    return response.json()


def fetch_wdi(indicator: str, start: int, end: int, country: str = "all") -> pd.DataFrame:
    """Fetch a World Bank indicator; preserve country code, year, source and units."""
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
    records: list[dict[str, Any]] = []
    page = 1
    while True:
        payload = get_json(url, {"date": f"{start}:{end}", "format": "json",
                                 "per_page": 20000, "page": page})
        if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
            break
        meta, rows = payload[0], payload[1]
        records.extend(rows)
        if page >= int(meta.get("pages", 1)):
            break
        page += 1
    df = pd.json_normalize(records)
    if df.empty:
        return df
    df["year"] = pd.to_numeric(df["date"], errors="coerce").astype("Int64")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["source_id"] = "WORLD_BANK_WDI"
    df["indicator_id"] = indicator
    df["retrieved_at_utc"] = pd.Timestamp.now(tz="UTC").isoformat()
    keep = [c for c in [
        "countryiso3code", "country.id", "country.value", "year", "value",
        "indicator.id", "indicator.value", "source_id", "indicator_id", "retrieved_at_utc"
    ] if c in df.columns]
    return df[keep]


def fetch_fred(series_id: str, start: str, end: str) -> pd.DataFrame:
    """Fetch a FRED series using the official API and environment-based secret."""
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise RuntimeError("Set FRED_API_KEY in your environment before fetching FRED.")
    payload = get_json(
        "https://api.stlouisfed.org/fred/series/observations",
        {"series_id": series_id, "api_key": api_key, "file_type": "json",
         "observation_start": start, "observation_end": end},
    )
    df = pd.DataFrame(payload.get("observations", []))
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["value"] = pd.to_numeric(df["value"].replace(".", pd.NA), errors="coerce")
        df["source_id"] = "FRED"
        df["series_id"] = series_id
        df["retrieved_at_utc"] = pd.Timestamp.now(tz="UTC").isoformat()
    return df


def save_table(df: pd.DataFrame, name: str) -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_parquet(RAW / f"{name}.parquet", index=False)
    df.to_csv(PROCESSED / f"{name}.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=2000)
    parser.add_argument("--end", type=int, default=2024)
    parser.add_argument("--wdi", default="NY.GDP.PCAP.CD",
                        help="World Bank indicator ID; default is GDP per capita, current US$")
    parser.add_argument("--fred-series", default="",
                        help="Optional FRED series ID, e.g. FEDFUNDS or SP500")
    parser.add_argument("--fred-start", default="2000-01-01")
    parser.add_argument("--fred-end", default="2024-12-31")
    args = parser.parse_args()

    wdi = fetch_wdi(args.wdi, args.start, args.end)
    save_table(wdi, f"wdi_{args.wdi.replace('.', '_')}")
    print(f"WDI {args.wdi}: {len(wdi)} rows")
    if args.fred_series:
        fred = fetch_fred(args.fred_series, args.fred_start, args.fred_end)
        save_table(fred, f"fred_{args.fred_series}")
        print(f"FRED {args.fred_series}: {len(fred)} rows")


if __name__ == "__main__":
    main()
