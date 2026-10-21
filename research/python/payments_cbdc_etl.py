#!/usr/bin/env python3
"""Evidence-first ETL for public CBDC, payments-rail, and U.S. regulatory sources.

This collector stores source observations and discovered links; it deliberately does
not infer CBDC status, sanctions exposure, or payment volume from page text alone.
Run: python research/python/payments_cbdc_etl.py --config configs/payments_cbdc_sources.yaml
Optional: pip install -r research/python/requirements-payments-etl.txt
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import re
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
import yaml
from bs4 import BeautifulSoup

LOG = logging.getLogger("globalblocs.payments_etl")
USER_AGENT = "GlobalBLOCSResearchBot/1.0 (+https://github.com/Whitney-Moss-ML-AI-Engineer/globalblocs-financial-intelligence)"
DEFAULT_TIMEOUT = 25
MAX_BYTES = 12_000_000
HEADERS = {"User-Agent": USER_AGENT, "Accept": "text/html,application/json,application/xml,*/*"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def robots_allowed(url: str, session: requests.Session, cache: dict[str, RobotFileParser]) -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    if robots_url not in cache:
        parser = RobotFileParser()
        parser.set_url(robots_url)
        try:
            response = session.get(robots_url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                parser.parse(response.text.splitlines())
            else:
                # A missing/unavailable robots file is not treated as explicit disallow.
                parser.parse([])
        except requests.RequestException:
            parser.parse([])
        cache[robots_url] = parser
    return cache[robots_url].can_fetch(USER_AGENT, url)


def fetch_url(url: str, session: requests.Session, robots_cache: dict[str, RobotFileParser],
              delay_seconds: float = 1.0) -> dict[str, Any]:
    """Fetch one public URL politely, recording audit data even for failures."""
    audit: dict[str, Any] = {
        "url": url, "retrieved_at_utc": utc_now(), "http_status": None,
        "content_type": None, "bytes": 0, "sha256": None, "etag": None,
        "last_modified": None, "fetch_status": "failed", "error": None,
    }
    if not robots_allowed(url, session, robots_cache):
        audit.update(fetch_status="skipped_robots", error="robots.txt disallows this URL")
        return {**audit, "body": b""}
    time.sleep(max(0.0, delay_seconds))
    try:
        response = session.get(url, headers=HEADERS, timeout=DEFAULT_TIMEOUT, stream=True)
        audit["http_status"] = response.status_code
        audit["content_type"] = response.headers.get("Content-Type", "")
        audit["etag"] = response.headers.get("ETag")
        audit["last_modified"] = response.headers.get("Last-Modified")
        chunks, size = [], 0
        for chunk in response.iter_content(chunk_size=65536):
            if not chunk:
                continue
            size += len(chunk)
            if size > MAX_BYTES:
                audit.update(fetch_status="skipped_size_limit", error=f"response exceeded {MAX_BYTES} bytes")
                response.close()
                return {**audit, "body": b""}
            chunks.append(chunk)
        body = b"".join(chunks)
        audit.update(bytes=len(body), sha256=sha256(body),
                     fetch_status="ok" if response.ok else "http_error")
        if not response.ok:
            audit["error"] = f"HTTP {response.status_code}"
        return {**audit, "body": body}
    except requests.RequestException as exc:
        audit["error"] = f"{type(exc).__name__}: {exc}"
        return {**audit, "body": b""}


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def extract_observations(source: dict[str, Any], fetched: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract source-level evidence and HTML table rows without guessing semantics."""
    if not fetched["body"] or fetched["fetch_status"] != "ok":
        return []
    content_type = (fetched.get("content_type") or "").lower()
    body = fetched["body"]
    text_body = body.decode("utf-8", errors="replace")
    source_id = source.get("source_id", source["name"].lower().replace(" ", "_"))
    base = {
        "source_id": source_id, "source_name": source["name"],
        "source_type": source.get("source_type", "reference"),
        "source_url": fetched["url"], "retrieved_at_utc": fetched["retrieved_at_utc"],
        "http_status": fetched["http_status"], "content_type": fetched["content_type"],
        "source_sha256": fetched["sha256"], "etag": fetched.get("etag"),
        "last_modified": fetched.get("last_modified"), "record_type": "source_observation",
        "country": "", "iso2": "", "iso3": "", "entity_name": "",
        "status": "", "status_date": "", "launch_date": "", "operator": "",
        "rail_type": "", "settlement_backend": "", "currency": "",
        "use_cases_json": "[]", "official_record_url": fetched["url"],
        "title": "", "text_excerpt": "", "table_json": "{}", "verification_status": "source_observation_only",
    }
    if "json" in content_type or text_body.lstrip().startswith(("{", "[")):
        try:
            obj = json.loads(text_body)
            base["title"] = source["name"]
            base["text_excerpt"] = clean_text(json.dumps(obj, ensure_ascii=False))[:1500]
            base["table_json"] = json.dumps(obj, ensure_ascii=False)[:20000]
            return [base]
        except json.JSONDecodeError:
            pass
    soup = BeautifulSoup(body, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "nav", "footer"]):
        tag.decompose()
    title = clean_text(soup.title.get_text(" ", strip=True)) if soup.title else source["name"]
    base["title"] = title
    base["text_excerpt"] = clean_text(soup.get_text(" ", strip=True))[:1500]
    observations = []
    for table_index, table in enumerate(soup.find_all("table")):
        rows = []
        for tr in table.find_all("tr")[:250]:
            cells = [clean_text(cell.get_text(" ", strip=True)) for cell in tr.find_all(["th", "td"])]
            if cells and any(cells):
                rows.append(cells)
        if rows:
            record = dict(base)
            record.update(record_type="html_table", table_json=json.dumps({"table_index": table_index, "rows": rows}, ensure_ascii=False),
                          text_excerpt=clean_text(" | ".join(" ".join(r) for r in rows))[:1500])
            observations.append(record)
    if not observations:
        observations.append(base)
    # Store discovered links as individual records so downstream enrichment can crawl them later.
    for anchor in soup.find_all("a", href=True):
        label = clean_text(anchor.get_text(" ", strip=True))
        link = urljoin(fetched["url"], anchor["href"].strip())
        if urlparse(link).scheme not in ("http", "https"):
            continue
        if not label:
            continue
        record = dict(base)
        record.update(record_type="discovered_link", entity_name=label[:250], official_record_url=link,
                      text_excerpt=label[:1500])
        observations.append(record)
    return observations


def write_outputs(records: list[dict[str, Any]], audits: list[dict[str, Any]], output_dir: Path,
                  sqlite_path: Path | None = None) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    # Stable, ingest-friendly files. JSONL preserves row-level source evidence.
    fields = sorted({key for row in records for key in row}) if records else [
        "source_id", "source_name", "source_type", "source_url", "retrieved_at_utc", "record_type"
    ]
    with (output_dir / "payments_cbdc_observations.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
    with (output_dir / "payments_cbdc_observations.jsonl").open("w", encoding="utf-8") as f:
        for row in records:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (output_dir / "source_audit.json").open("w", encoding="utf-8") as f:
        json.dump(audits, f, indent=2, ensure_ascii=False)
    if sqlite_path:
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(sqlite_path) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS source_observation (
                observation_id INTEGER PRIMARY KEY,
                source_id TEXT, source_name TEXT, source_type TEXT, source_url TEXT,
                retrieved_at_utc TEXT, http_status INTEGER, content_type TEXT,
                source_sha256 TEXT, record_type TEXT, country TEXT, iso2 TEXT, iso3 TEXT,
                entity_name TEXT, status TEXT, status_date TEXT, launch_date TEXT,
                operator TEXT, rail_type TEXT, settlement_backend TEXT, currency TEXT,
                use_cases_json TEXT, official_record_url TEXT, title TEXT, text_excerpt TEXT,
                table_json TEXT, verification_status TEXT, raw_json TEXT NOT NULL
            )""")
            for row in records:
                cols = ["source_id","source_name","source_type","source_url","retrieved_at_utc","http_status",
                        "content_type","source_sha256","record_type","country","iso2","iso3","entity_name",
                        "status","status_date","launch_date","operator","rail_type","settlement_backend","currency",
                        "use_cases_json","official_record_url","title","text_excerpt","table_json","verification_status"]
                conn.execute("INSERT INTO source_observation (" + ",".join(cols) + ",raw_json) VALUES (" +
                             ",".join("?" for _ in range(len(cols)+1)) + ")",
                             [row.get(c) for c in cols] + [json.dumps(row, ensure_ascii=False)])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/payments_cbdc_sources.yaml")
    parser.add_argument("--output-dir", default="data/raw/payments_cbdc")
    parser.add_argument("--sqlite", default="data/processed/payments_cbdc.sqlite")
    parser.add_argument("--no-sqlite", action="store_true")
    parser.add_argument("--delay", type=float, default=1.0, help="Minimum delay before each source request")
    parser.add_argument("--source-id", action="append", help="Only run named source_id (repeatable)")
    parser.add_argument("--max-sources", type=int, default=0, help="Optional limit for smoke tests")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    config_path = Path(args.config)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    sources = [s for s in config.get("sources", []) if s.get("enabled", True)]
    if args.source_id:
        selected = set(args.source_id)
        sources = [s for s in sources if s.get("source_id") in selected]
    if args.max_sources:
        sources = sources[:args.max_sources]
    session = requests.Session()
    robots_cache: dict[str, RobotFileParser] = {}
    records, audits = [], []
    for source in sources:
        LOG.info("Fetching %s (%s)", source["name"], source["url"])
        result = fetch_url(source["url"], session, robots_cache, args.delay)
        audit = {k: v for k, v in result.items() if k != "body"}
        audit.update(source_id=source.get("source_id"), source_name=source["name"])
        audits.append(audit)
        extracted = extract_observations(source, result)
        records.extend(extracted)
        LOG.info("status=%s extracted=%d", result["fetch_status"], len(extracted))
    write_outputs(records, audits, Path(args.output_dir), None if args.no_sqlite else Path(args.sqlite))
    LOG.info("Complete: %d observations across %d sources", len(records), len(sources))
    return 0 if any(a["fetch_status"] == "ok" for a in audits) or not sources else 2


if __name__ == "__main__":
    raise SystemExit(main())
