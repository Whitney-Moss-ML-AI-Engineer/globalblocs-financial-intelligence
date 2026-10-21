# GlobalBLOCS Payments, CBDC, and Regulatory ETL

## Purpose and boundaries

This pipeline collects **public source observations** for CBDC programs, payment rails, sanctions resources, and U.S. regulatory documents. It writes CSV, JSONL, source-audit JSON, and an optional SQLite database. The first implementation is intentionally evidence-first: it records page content, tables, links, HTTP metadata, timestamps, and hashes. It does not pretend a generic HTML parser can reliably infer a country's CBDC status from arbitrary prose.

## Run locally

From the repository root:

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r research/python/requirements-payments-etl.txt
python research/python/payments_cbdc_etl.py
```

Optional smoke test:

```bash
python research/python/payments_cbdc_etl.py --max-sources 2 --delay 0
```

Outputs default to:
- `data/raw/payments_cbdc/payments_cbdc_observations.csv`
- `data/raw/payments_cbdc/payments_cbdc_observations.jsonl`
- `data/raw/payments_cbdc/source_audit.json`
- `data/processed/payments_cbdc.sqlite`

Do not commit live crawls, downloaded sanctions lists, credentials, or large raw files without reviewing repository data policy.

## Pipeline stages

1. **Source registry** — `configs/payments_cbdc_sources.yaml` lists official regulators, central banks, tracker pages, payment networks, and standards-related references.
2. **Extract** — Requests fetches public pages with a descriptive user agent, timeout, byte cap, delay, robots.txt check, and HTTP audit metadata. BeautifulSoup extracts titles, tables, and discovered links. The current implementation is a seed collector, not a full domain spider.
3. **Transform** — Normalize whitespace and URLs; preserve the original source URL, retrieval timestamp, ETag, Last-Modified, content hash, and unmodified table structure. It does not fill unknown values or treat tracker claims as official central-bank confirmation.
4. **Load** — CSV and JSONL for portable ingestion; SQLite for local queries. PostgreSQL is the recommended production store after schema/migrations and deduplication policy are finalized.
5. **Enrich** — Add source-specific adapters for Atlantic Council tracker data, CBDCTracker.org, Federal Register API, Congress.gov API, OFAC downloadable lists, NPCI monthly statistics, and official central-bank releases. Prefer documented APIs or official downloads over browser scraping.
6. **Schedule/observe** — Run weekly for active tracker and sanctions data, monthly for broad country coverage, and event-driven for new executive orders or OFAC list releases. Store each observation as an immutable snapshot and alert on source hash changes.

## Scraping and browser tools

- **Requests**: default for static pages, JSON endpoints, and downloadable documents.
- **BeautifulSoup**: parse HTML/XML after retrieval.
- **Scrapy**: add when the crawl needs domain-scoped queues, concurrency controls, retries, and many linked pages.
- **Selenium or Pyppeteer**: last resort for JavaScript-only interfaces. Inspect the site's network calls first; if a public JSON endpoint exists, call it directly within the site's terms.
- **Pandas**: useful for tabular cleaning after extraction; do not let automatic type inference erase identifiers or leading zeros.

The initial collector uses Requests + BeautifulSoup. Scrapy, Selenium, and Pyppeteer are listed as optional extensions, not falsely represented as implemented.

## Canonical data model

Separate entities from observations. Recommended production tables:

- `jurisdiction`: ISO-3166 codes, preferred name, valid-from/to.
- `cbdc_project`: jurisdiction, project name, retail/wholesale, status, status effective date, launch date, legal basis, official project URL.
- `payment_rail`: operator, jurisdiction, messaging/clearing/settlement role, supported currencies, settlement asset, operating status, participation model.
- `rail_participant`: participant organization, rail, role, country, valid-from/to, source.
- `rail_corridor`: origin/destination jurisdiction, currencies, supported use case, rail(s), operational status, effective dates.
- `regulatory_document`: issuing body, document number, type, publication/effective dates, title, official URL, topic tags, status.
- `sanctions_program` and `sanctions_list_snapshot`: authority, list/program identifier, release date, source hash; protect personal data and retain official identifiers.
- `source` and `source_observation`: source URL, retrieval timestamp, hash, HTTP metadata, parser version, extracted payload, verification level.
- `risk_assessment`: model version, assessment date, factors, scores, uncertainty, evidence links, reviewer status.

Use ISO dates and UTC timestamps. Store original values and normalized values side-by-side. Maintain source-specific lineage and record corrections instead of overwriting history.

## Executive Order and regulatory risk scoring

Use an explainable 0–100 **screening score**, not a legal conclusion or a prediction of enforcement:

`Risk = 0.25*LegalScope + 0.20*PaymentRailExposure + 0.20*JurisdictionExposure + 0.15*ImplementationUrgency + 0.10*OperationalDependency + 0.10*EvidenceConfidenceAdjustment`

Each factor is normalized 0–100. The evidence-confidence factor should reduce confidence in the score when source coverage is weak; it should not automatically raise a substantive risk score. Better production design: publish a risk score and a separate confidence score. Store per-factor rationale, cited document IDs, model version, analyst review, and as-of time. Do not assign a country or rail a blanket “sanctions resistant” label: sanctions exposure depends on jurisdiction, counterparties, currency, ownership, correspondent relationships, and the specific legal authority.

Recommended risk dimensions:
- legal scope and effective date;
- payment rail and intermediary dependencies;
- sanctioned-party/jurisdiction nexus;
- USD clearing and correspondent-bank dependency;
- operator, participant, and technology concentration;
- cross-border data/reporting obligations;
- transition period, exceptions, licenses, and wind-down terms;
- source quality and whether legal interpretation has been reviewed.

## Comparison framework for payment systems

Do not compare unlike categories as if they were equivalent:

| System | Primary function | Currency / asset | Key distinction |
|---|---|---|---|
| SWIFT | Financial messaging | Multiple currencies; not itself settlement money | Messages route through participating institutions; settlement occurs through banks and payment systems |
| CIPS | RMB cross-border clearing/settlement infrastructure with messaging capabilities | RMB | China-centered infrastructure; participation and message paths should be verified from current CIPS documentation |
| SPFS | Financial messaging system operated by the Bank of Russia | Multiple message use cases; not a universal settlement asset | Messaging alternative, not a direct equivalent to all functions of SWIFT or CIPS |
| mBridge | Multi-CBDC wholesale cross-border settlement project/platform | Participating central-bank money/tokenized representations, per project rules | Project participation and operational status are time-sensitive; do not infer universal availability |
| INSTEX | Historical trade-support clearing mechanism | No standalone currency/payment rail | Defunct/liquidated; retain as historical case, not an active network |
| UPI | Indian instant retail payment system | Bank deposits and supported payment instruments; CBDC integration must be separately evidenced | Retail payment interface/rail, not a CBDC itself |
| Fedwire Funds Service | U.S. wholesale funds transfer service | USD central-bank money settlement | Domestic high-value settlement |
| CHIPS | Private-sector USD clearing and settlement system | USD | Separate from SWIFT messaging |
| CBDC | A form of central-bank money | Depends on issuing jurisdiction | A monetary instrument; not by itself a messaging or payment network |

The matrix is a taxonomy, not a claim that every rail has equivalent sanctions exposure or cross-border reach.

## De-dollarization infrastructure stack

```text
User / merchant / treasury application
              |
        PSP / commercial bank
              |
   Routing and financial messaging
   (e.g., SWIFT, SPFS; ISO 20022 messages)
              |
   Clearing and settlement infrastructure
   (e.g., Fedwire, CHIPS, CIPS, domestic instant rails)
              |
   Settlement asset and currency
   (commercial-bank deposits, central-bank reserves,
    eligible tokenized deposits or CBDC where implemented)
              |
   Legal authority, governance, access rules,
   AML/CFT controls, sanctions, dispute resolution
```

Actual deployments can combine or reorder layers. Do not depict a CBDC bridge as live production infrastructure unless the project operator documents that status.

## Sanctions exposure heat map design

A rail-only label such as “low/high” is too simplistic. Score a *transaction scenario* using:
- parties and beneficial ownership;
- origin/destination jurisdictions;
- currency and correspondent-bank path;
- payment network and settlement operators;
- goods/services and applicable restrictions;
- licenses, exemptions, and effective dates.

Output: `scenario_id, as_of_date, origin, destination, currency, counterparties_review_status, rail_path, usd_clearing_dependency, sanctions_nexus, legal_source_ids, exposure_score, confidence_score, reviewer_status`.

Use heat-map colors only as a visual encoding of a documented, versioned scoring method. The tool must flag for compliance review and must not advise users how to evade sanctions or screen around legal restrictions.

## Limitations and production checklist

- Generic extraction is not the same as verified country-level CBDC data.
- Interactive tracker pages may require a source-specific JSON adapter; do not assume the HTML contains the complete country table.
- The current seed registry includes public starting URLs, not a verified complete list of 130+ jurisdictions.
- Verify every endpoint, robots policy, terms, rate limits, data license, and current official status before production scheduling.
- Federal Register and Congress.gov have documented APIs; use official APIs and store document identifiers and publication/effective dates.
- OFAC list snapshots must include the list version/publication timestamp and cryptographic hash; do not rely on search-engine snippets.
- Add automated tests for parsers, schema validation, duplicate handling, source freshness, and change detection.
- Never report that a source crawl succeeded, that all jurisdictions were captured, or that an assessment is legally authoritative unless verified by execution and review.
