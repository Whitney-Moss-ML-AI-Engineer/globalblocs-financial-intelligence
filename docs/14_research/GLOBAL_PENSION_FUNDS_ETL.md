# GlobalBLOCS — Global Pension Funds ETL

## Objective

Create a source-traceable dataset of the largest global pension funds, with a target universe of 300 funds. The pipeline is designed to ingest public HTML tables and linked PDF reports, normalize records, preserve source lineage, and emit CSV/JSONL plus an audit log.

**Important:** the target of 300 is a target, not a claim that a single freely accessible web page currently exposes all 300 records. The Thinking Ahead Institute / Pensions & Investments ranking and fund annual reports may have different publication years, definitions, currencies, and reuse terms. Check source terms and licensing before bulk extraction or redistribution.

## Run

From the repository root:

```bash
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r research/python/requirements-pension-etl.txt
python research/python/top300_pension_funds_etl.py
```

Provide additional source pages or report PDFs by repeating `--source-url`:

```bash
python research/python/top300_pension_funds_etl.py \
  --source-url "https://example.org/public-ranking.html" \
  --source-url "https://example.org/annual-report.pdf" \
  --out-dir data/raw/pension_funds
```

The default URL is a starting point for source discovery, not a guaranteed machine-readable ranking endpoint. The scraper may correctly return zero records if the page contains no extractable table. Check `source_audit.json` and the source report before interpreting output.

## Outputs

- `pension_funds.csv`: normalized flat file.
- `pension_funds.jsonl`: newline-delimited JSON for incremental pipelines.
- `source_audit.json`: retrieval time, HTTP status, content type, bytes, SHA-256, extraction method, count and status.
- Downloaded PDF copies (when applicable) are stored with content-hash filenames under the output directory.

## Core fields

| Field | Meaning |
|---|---|
| `rank` | Rank as published by the source; do not merge ranks across editions without a ranking-year field. |
| `fund_name` | Published institution/fund name. |
| `country` | Source-reported country or jurisdiction; retain source wording until a validated ISO crosswalk is applied. |
| `aum_value` | Parsed reported amount in the source's stated unit. |
| `aum_currency` | ISO-like currency code only when supported by the source. Ambiguous dollar symbols are flagged rather than silently converted. |
| `aum_usd` | Intentionally blank until a documented FX rate and conversion date are applied. |
| `fund_type` | Public/corporate/multi-employer/other only when source evidence supports classification. |
| `sector_focus` | Source-reported field; not inferred from the fund's country. |
| `as_of_date` | Source reporting date/year where available. |
| `source_url`, `source_document_url` | Traceable page and report links. |
| `retrieved_at_utc`, `source_row_hash` | Retrieval lineage and duplicate detection. |
| `verification_status`, `notes` | Human review flags and parsing caveats. |

## Data quality rules

1. Do not treat the latest publication as a live AUM feed; preserve ranking edition and reporting date.
2. Do not interpret missing AUM or currency as zero.
3. Never convert currency based on a symbol alone. To populate USD AUM, store original amount/currency, FX source, rate, FX date, conversion method and converted value.
4. Do not infer pension plan type, sector allocation, risk, or ESG rating from a fund name. Capture only evidence-backed fields with source references.
5. Preserve historical snapshots rather than overwriting prior editions.
6. Resolve parent/child funds, consolidated funds, and duplicate names with stable IDs after review.
7. Respect website terms, robots policies, copyright, API limits, and licensing. Public availability does not automatically grant bulk redistribution rights.
8. Keep scraped values marked `needs_source_review` until checked against the original source.

## Limitations and planned extensions

- HTML table extraction is heuristic; complex multi-row tables may need source-specific parsers.
- PDF extraction is best-effort and may require manual review.
- XLS/XLSX links are discovered but not currently parsed by this starter.
- IMF/BIS/FRED/FX integrations are not needed for the initial ranking extraction and should be separate adapters with their own source-specific metadata.
- A production run should add tests, schema validation, stable fund IDs, ranking edition, explicit units (million/billion/trillion), ISO 3166 country crosswalks, FX conversion with provenance, incremental updates, retry/backoff, and a reviewed source registry.
- The code does not claim that 300 records were retrieved until a run actually extracts and verifies 300 distinct eligible funds.

## Database integration

Suggested normalized tables:

- `pension_fund`: stable fund ID, canonical name, jurisdiction ID, fund type.
- `pension_fund_snapshot`: fund ID, ranking edition, rank, AUM value, currency, AUM as-of date, source record hash.
- `pension_fund_source`: URL, publisher, publication date, retrieval timestamp, content hash, license/terms note.
- `pension_fund_asset_allocation`: fund ID, snapshot date, asset class, allocation share, currency and source evidence.

AUM is a stock measured at a date; flows and annual performance are separate measures and must not be conflated.
