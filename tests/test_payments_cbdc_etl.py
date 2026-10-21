"""Unit tests for conservative payments/CBDC ETL transformations."""
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "research" / "python" / "payments_cbdc_etl.py"
spec = importlib.util.spec_from_file_location("payments_cbdc_etl", SCRIPT)
etl = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = etl
spec.loader.exec_module(etl)


def test_clean_text_collapses_whitespace():
    assert etl.clean_text("  central\n bank   digital currency ") == "central bank digital currency"


def test_hash_is_stable():
    assert etl.sha256(b"evidence") == etl.sha256(b"evidence")
    assert len(etl.sha256(b"evidence")) == 64


def test_html_table_and_links_are_extracted():
    html = b"""<!doctype html><html><head><title>Example tracker</title></head><body>
    <table><tr><th>Country</th><th>Status</th></tr><tr><td>Exampleland</td><td>Pilot</td></tr></table>
    <a href="/cbdc/project">Project page</a></body></html>"""
    source = {"source_id": "test", "name": "Example", "source_type": "tracker"}
    fetched = {
        "url": "https://example.org/tracker", "retrieved_at_utc": "2026-01-01T00:00:00+00:00",
        "http_status": 200, "content_type": "text/html", "sha256": etl.sha256(html),
        "etag": None, "last_modified": None, "fetch_status": "ok", "body": html,
    }
    rows = etl.extract_observations(source, fetched)
    assert any(r["record_type"] == "html_table" for r in rows)
    link = next(r for r in rows if r["record_type"] == "discovered_link")
    assert link["official_record_url"] == "https://example.org/cbdc/project"
    assert rows[0]["title"] == "Example tracker"


def test_failed_fetch_produces_no_observations():
    fetched = {"body": b"", "fetch_status": "failed", "url": "https://example.org",
               "retrieved_at_utc": "2026-01-01T00:00:00+00:00"}
    assert etl.extract_observations({"name": "Example"}, fetched) == []
