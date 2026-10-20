#!/usr/bin/env python3
"""Research-grade starter ETL for a global pension-fund universe.

The pipeline discovers HTML tables and linked report files from configured
public URLs, normalizes records conservatively, and writes CSV/JSONL plus a
source-audit log. It does NOT assume every source page contains a Top 300
table or that every AUM value is USD. Validate licensing and source terms
before collecting or redistributing report contents.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

LOG = logging.getLogger("top300_pension_funds")
DEFAULT_SOURCE = (
    "https://www.thinkingaheadinstitute.org/news/article/"
    "top-pension-funds-reach-all-time-global-record/"
)
USER_AGENT = "GlobalBLOCSResearchBot/1.0 (public research; contact repository owner)"
TIMEOUT = 30
PAUSE_SECONDS = 1.0

ALIASES = {
    "rank": {"rank", "ranking", "position", "no.", "no"},
    "fund_name": {"fund", "fund name", "pension fund", "institution", "name", "organisation", "organization"},
    "country": {"country", "location", "country/region", "region"},
    "aum": {"aum", "assets under management", "total assets", "assets", "fund assets"},
    "currency": {"currency", "ccy"},
    "fund_type": {"fund type", "type", "plan type", "pension type"},
    "sector_focus": {"sector focus", "sector", "industry focus"},
    "as_of_date": {"as of", "as of date", "reporting date", "year", "date"},
}
COLUMNS = [
    "rank", "fund_name", "country", "aum_value", "aum_currency",
    "aum_usd", "fund_type", "sector_focus", "as_of_date",
    "source_name", "source_url", "source_document_url", "retrieved_at_utc",
    "source_row_hash", "extraction_method", "verification_status", "notes",
]


@dataclass
class SourceAudit:
    source_url: str
    retrieved_at_utc: str
    http_status: int | None
    content_type: str | None
    bytes_received: int
    sha256: str | None
    extraction_method: str
    records_extracted: int
    status: str
    message: str = ""


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalized_header(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value).strip().lower().replace("\n", " "))


def map_columns(columns: list[Any]) -> dict[Any, str]:
    mapped: dict[Any, str] = {}
    for col in columns:
        h = normalized_header(col)
        for target, aliases in ALIASES.items():
            if h in aliases:
                mapped[col] = target
                break
    return mapped


def parse_number(value: Any) -> float | None:
    """Parse a number while retaining currency separately; never guess units."""
    if value is None or pd.isna(value):
        return None
    s = str(value).strip()
    if not s or s.lower() in {"n/a", "na", "not available", "-", "—", "null"}:
        return None
    negative = s.startswith("(") and s.endswith(")")
    s = s.strip("()").replace(",", "").replace(" ", "")
    multiplier = 1.0
    match = re.search(r"(?i)(bn|billion|b|mn|million|m|tn|trillion|t)$", s)
    if match:
        token = match.group(1).lower()
        multiplier = 1e12 if token in {"tn", "trillion", "t"} else 1e9 if token in {"bn", "billion", "b"} else 1e6
        s = s[:match.start()]
    s = re.sub(r"[^0-9.\-]", "", s)
    try:
        n = float(s) * multiplier
        return -n if negative else n
    except ValueError:
        return None


def extract_currency(value: Any, explicit: Any = None) -> str | None:
    if explicit is not None and not pd.isna(explicit):
        c = str(explicit).strip().upper()
        if re.fullmatch(r"[A-Z]{3}", c):
            return c
    s = str(value or "")
    if "US$" in s or "USD" in s.upper() or "$" in s:
        return "USD"  # Dollar symbols are ambiguous; flagged in notes below.
    if "€" in s or "EUR" in s.upper():
        return "EUR"
    if "£" in s or "GBP" in s.upper():
        return "GBP"
    if "¥" in s or "JPY" in s.upper():
        return "JPY"
    if "C$" in s or "CAD" in s.upper():
        return "CAD"
    if "A$" in s or "AUD" in s.upper():
        return "AUD"
    return None


def source_hash(source_url: str, row: dict[str, Any]) -> str:
    payload = json.dumps({"url": source_url, "row": row}, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def fetch(session: requests.Session, url: str) -> requests.Response:
    response = session.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    return response


def table_to_records(table: pd.DataFrame, page_url: str, doc_url: str, source_name: str) -> list[dict[str, Any]]:
    if table.empty:
        return []
    table = table.copy()
    # pandas may return multi-level headers from complex HTML tables.
    if isinstance(table.columns, pd.MultiIndex):
        table.columns = [" ".join(str(x) for x in col if str(x) != "nan").strip() for col in table.columns]
    mapping = map_columns(list(table.columns))
    if "fund_name" not in mapping.values():
        # Try first row as header for poorly structured HTML tables.
        first = table.iloc[0].tolist()
        alt = map_columns(first)
        if "fund_name" in alt.values():
            table.columns = first
            table = table.iloc[1:].reset_index(drop=True)
            mapping = alt
    if "fund_name" not in mapping.values():
        return []
    out: list[dict[str, Any]] = []
    retrieved = now_utc()
    for _, row in table.iterrows():
        raw = {str(k): (None if pd.isna(v) else str(v).strip()) for k, v in row.items()}
        rec = {v: raw.get(str(k)) for k, v in mapping.items()}
        name = rec.get("fund_name")
        if not name or name.lower() in {"fund", "fund name", "total", "source"}:
            continue
        aum_raw = rec.get("aum")
        explicit_ccy = rec.get("currency")
        currency = extract_currency(aum_raw, explicit_ccy)
        amount = parse_number(aum_raw)
        notes = []
        if currency == "USD" and aum_raw and "$" in aum_raw and "US$" not in aum_raw and "USD" not in aum_raw.upper():
            notes.append("Dollar symbol ambiguous; verify currency against source.")
            currency = None
        if amount is None:
            notes.append("AUM not parsed; inspect original source.")
        if not rec.get("country"):
            notes.append("Country not supplied by extracted table.")
        normalized = {
            "rank": parse_number(rec.get("rank")),
            "fund_name": str(name).strip(),
            "country": rec.get("country"),
            "aum_value": amount,
            "aum_currency": currency,
            "aum_usd": None,  # only populate with documented FX conversion + date
            "fund_type": rec.get("fund_type"),
            "sector_focus": rec.get("sector_focus"),
            "as_of_date": rec.get("as_of_date"),
            "source_name": source_name,
            "source_url": page_url,
            "source_document_url": doc_url,
            "retrieved_at_utc": retrieved,
            "extraction_method": "html_table",
            "verification_status": "needs_source_review",
            "notes": " ".join(notes) or None,
        }
        normalized["source_row_hash"] = source_hash(doc_url, raw)
        out.append(normalized)
    return out


def discover_documents(soup: BeautifulSoup, page_url: str) -> list[str]:
    found = []
    for a in soup.select("a[href]"):
        href = urljoin(page_url, a.get("href", ""))
        label = (a.get_text(" ", strip=True) + " " + href).lower()
        if urlparse(href).scheme not in {"http", "https"}:
            continue
        if any(ext in href.lower().split("?")[0] for ext in (".pdf", ".xlsx", ".xls", ".csv")) or (
            "top 300" in label and any(word in label for word in ("download", "report", "data", "pdf", "excel"))
        ):
            found.append(href)
    return sorted(set(found))


def parse_pdf_tables(pdf_path: Path, source_url: str, page_url: str, source_name: str) -> list[dict[str, Any]]:
    """Optional PDF table extraction; tries pdfplumber then camelot if installed."""
    records: list[dict[str, Any]] = []
    try:
        import pdfplumber  # type: ignore
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                for rows in (page.extract_tables() or []):
                    if len(rows) < 2:
                        continue
                    frame = pd.DataFrame(rows[1:], columns=rows[0])
                    records.extend(table_to_records(frame, page_url, source_url, source_name))
        if records:
            return records
    except ImportError:
        LOG.info("pdfplumber not installed; trying camelot if available")
    except Exception as exc:
        LOG.warning("pdfplumber extraction issue for %s: %s", source_url, exc)
    try:
        import camelot  # type: ignore
        tables = camelot.read_pdf(str(pdf_path), pages="all", flavor="stream")
        for item in tables:
            frame = item.df
            if len(frame) > 1:
                frame.columns = frame.iloc[0]
                records.extend(table_to_records(frame.iloc[1:], page_url, source_url, source_name))
    except ImportError:
        LOG.warning("Install pdfplumber or camelot to parse PDFs: %s", source_url)
    except Exception as exc:
        LOG.warning("camelot extraction issue for %s: %s", source_url, exc)
    return records


def run_source(source_url: str, source_name: str, output_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    audits: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    try:
        response = fetch(session, source_url)
        content = response.content
        content_type = response.headers.get("Content-Type", "")
        digest = hashlib.sha256(content).hexdigest()
        if "pdf" in content_type.lower() or source_url.lower().split("?")[0].endswith(".pdf"):
            output_dir.mkdir(parents=True, exist_ok=True)
            local_pdf = output_dir / f"source_{digest[:12]}.pdf"
            local_pdf.write_bytes(content)
            records.extend(parse_pdf_tables(local_pdf, source_url, source_url, source_name))
            method = "pdf_tables"
            status = "ok" if records else "fetched_no_records"
        else:
            soup = BeautifulSoup(content, "html.parser")
            try:
                tables = pd.read_html(response.text)
            except ValueError:
                tables = []
            for table in tables:
                records.extend(table_to_records(table, source_url, source_url, source_name))
            # Download and parse linked PDFs only; spreadsheet links are recorded
            # for a future parser rather than being silently misread.
            for doc_url in discover_documents(soup, source_url):
                time.sleep(PAUSE_SECONDS)
                try:
                    doc_response = fetch(session, doc_url)
                    if "pdf" in doc_response.headers.get("Content-Type", "").lower() or doc_url.lower().split("?")[0].endswith(".pdf"):
                        doc_hash = hashlib.sha256(doc_response.content).hexdigest()
                        output_dir.mkdir(parents=True, exist_ok=True)
                        local_pdf = output_dir / f"source_{doc_hash[:12]}.pdf"
                        local_pdf.write_bytes(doc_response.content)
                        records.extend(parse_pdf_tables(local_pdf, doc_url, source_url, source_name))
                except Exception as exc:
                    LOG.warning("Linked document failed %s: %s", doc_url, exc)
            method = "html_tables_and_linked_pdfs"
            status = "ok" if records else "fetched_no_matching_tables"
        audits.append(asdict(SourceAudit(
            source_url=source_url, retrieved_at_utc=now_utc(),
            http_status=response.status_code, content_type=content_type,
            bytes_received=len(content), sha256=digest, extraction_method=method,
            records_extracted=len(records), status=status,
            message="Extracted values require validation against original report.",
        )))
    except Exception as exc:
        LOG.exception("Source failed: %s", source_url)
        audits.append(asdict(SourceAudit(
            source_url=source_url, retrieved_at_utc=now_utc(),
            http_status=None, content_type=None, bytes_received=0, sha256=None,
            extraction_method="none", records_extracted=0, status="error", message=str(exc),
        )))
    finally:
        session.close()
    return records, audits


def normalize_dataset(records: list[dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame(columns=COLUMNS)
    for col in COLUMNS:
        if col not in df:
            df[col] = None
    df = df[COLUMNS]
    df["rank"] = pd.to_numeric(df["rank"], errors="coerce").astype("Int64")
    df["aum_value"] = pd.to_numeric(df["aum_value"], errors="coerce")
    df["aum_usd"] = pd.to_numeric(df["aum_usd"], errors="coerce")
    df["fund_name"] = df["fund_name"].astype("string").str.strip()
    df["country"] = df["country"].astype("string").str.strip()
    df["aum_currency"] = df["aum_currency"].astype("string").str.upper()
    # Keep repeated names from distinct source/year records; deduplicate exact source rows.
    return df.drop_duplicates(subset=["source_row_hash"], keep="last").reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-url", action="append", dest="sources", help="Source page/PDF URL; repeat to add sources.")
    parser.add_argument("--source-name", default="Thinking Ahead Institute / public reports")
    parser.add_argument("--out-dir", default="data/raw/pension_funds")
    parser.add_argument("--target-count", type=int, default=300)
    args = parser.parse_args()
    output_dir = Path(args.out_dir)
    urls = args.sources or [os.getenv("GLOBALBLOCS_PENSION_SOURCE_URL", DEFAULT_SOURCE)]
    all_records: list[dict[str, Any]] = []
    all_audits: list[dict[str, Any]] = []
    for url in urls:
        recs, audits = run_source(url, args.source_name, output_dir)
        all_records.extend(recs)
        all_audits.extend(audits)
        time.sleep(PAUSE_SECONDS)
    df = normalize_dataset(all_records)
    output_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_dir / "pension_funds.csv", index=False)
    df.to_json(output_dir / "pension_funds.jsonl", orient="records", lines=True, force_ascii=False)
    (output_dir / "source_audit.json").write_text(json.dumps(all_audits, indent=2), encoding="utf-8")
    # This reports the count honestly; it does not pad a partial scrape to 300.
    distinct = df["fund_name"].dropna().nunique() if not df.empty else 0
    print(f"Saved {len(df)} source records ({distinct} distinct fund names). Target: {args.target_count}.")
    print(f"Output: {output_dir.resolve()}")
    if distinct < args.target_count:
        print("WARNING: target not reached. Add licensed/public source URLs and manually verify extracted records.")
    if not df.empty:
        print("AUM USD populated:", int(df["aum_usd"].notna().sum()), "(currency conversion is deliberately not guessed).")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    main()
