# GlobalBLOCS Energy Intelligence

## Purpose
A first-class domain covering oil, natural gas, exploration and production, oilfield services, pipelines and midstream, refining, LNG, natural-gas utilities, and electric utilities with material fuel exposure.

## Dashboard workspaces
- Commodity benchmarks: WTI, Brent, Henry Hub, RBOB gasoline and heating-oil/ULSD proxies.
- Company universe: integrated producers, upstream, oilfield services, midstream, refiners, gas utilities and electric utilities.
- Market performance: historical observations and returns through the optional yfinance research adapter.
- EIA data explorer: server-side API access for petroleum prices/stocks/production, natural gas prices/storage and LNG datasets.
- Planned infrastructure research: pipeline operators, mileage, incidents, refineries, storage, processing plants, LNG terminals and utility service territories.

## Source hierarchy
1. EIA: official energy supply, demand, prices, inventories, storage and exports.
2. SEC EDGAR/XBRL: issuer financial statements, segment reporting, debt, capital expenditure, reserves disclosures and risk factors.
3. PHMSA: public pipeline operator, mileage, incident and safety datasets.
4. FERC: regulated gas/electric utility and oil/gas pipeline filings and market data.
5. CFTC: futures positioning and Commitments of Traders.
6. yfinance: convenience historical market observations only; not a licensed real-time exchange feed or authoritative fundamental source.

## Company segmentation
- Integrated: diversified upstream/downstream groups.
- Upstream: reserves, production mix, lifting costs, hedges and decline rates.
- Services: rig counts, utilization, backlog and margins.
- Midstream: throughput, fee-based revenue, capacity utilization, leverage and cash distributions.
- Refining: utilization, throughput, product yields and crack spreads.
- Gas utilities: rate base, allowed return, customer growth, weather-normalized volumes and capital expenditure.
- Electric utilities: generation mix, gas fuel exposure, load growth, rate base and regulatory recovery.

## API contracts
- GET /api/v1/energy/universe?segment=midstream
- GET /api/v1/energy/catalog
- GET /api/v1/energy/market-data?symbols=XOM,SR,AEE,CL=F,BZ=F,NG=F&period=1y
- POST /api/v1/energy/eia/query
- GET /api/v1/energy/sec/company/{ticker}/facts

The EIA query accepts a dataset ID from the catalog and a params object containing EIA API query parameters/facets. The key is read only from server-side EIA_API_KEY. Check EIA category/facet metadata before selecting facet codes; the implementation intentionally does not guess universal series IDs.

The SEC company facts endpoint resolves a ticker through the SEC company ticker directory, then retrieves its public XBRL Company Facts JSON. Configure SEC_USER_AGENT with an identifying application name and contact email. The starter mapping returns annual observations for revenue, operating income, net income, assets, operating cash flow, capital expenditures, noncurrent long-term debt and equity, including fiscal period, filing form, filed date, accession number, unit and source concept. SEC XBRL taxonomy extensions and company-specific tags may require future issuer-specific mappings. This endpoint currently retrieves facts on request; it does not yet persist them into the energy Gold layer.

## Infrastructure and safety source integration

The infrastructure source catalog exposes public PHMSA pipeline incident downloads, mileage/facility summaries, operator-directory information, LNG plant summaries and flagged incident trend files. PHMSA incident files are downloadable source artifacts with accompanying field definitions; a production ETL must inspect each release's data dictionary, preserve original fields, normalize incident categories and avoid mixing reporting populations or changed reporting thresholds.

Detailed National Pipeline Mapping System (NPMS) GIS information is restricted. The dashboard links only to public PHMSA summaries and the public map/operator directory. It does not ingest or expose restricted pipeline geometry, sensitive facility attributes or protected critical-infrastructure information.

FERC integration uses the official Data.FERC.gov API. Configure FERC_API_KEY server-side. The API's data-assets catalog is queried dynamically because dataset IDs may change; details are then fetched by the returned dataset ID. The initial implementation discovers metadata and does not automatically download every dataset, since some datasets can be large and may not support filtered subsets. FERC API keys are private and must never be sent to the browser.

The infrastructure database extension adds a source-preserving incident fact table and operator-performance fact table. Incident rows retain the original JSON record, source dataset/version/file, operator identifiers, incident/report dates, state/county, commodity, cause, consequence fields and units. The import process must be driven by the data dictionary for each PHMSA release; field names and reporting definitions must not be assumed identical across all report families.

### PHMSA incident file normalization

The repository includes a source-mapped CSV/TSV normalization CLI:

```bash
python scripts/energy/import_phmsa_incidents.py \
  --input /path/to/phmsa_release.txt \
  --mapping configs/phmsa_incident_mapping.template.json \
  --output /path/to/phmsa_incidents.normalized.jsonl \
  --dataset gas_transmission_incidents \
  --delimiter tab \
  --source-version 2026-release \
  --source-url https://www.phmsa.dot.gov/data-and-statistics/pipeline/distribution-transmission-gathering-lng-and-liquid-accident-and-incident-data
```

Before running it, copy/edit the mapping template to match the exact source headers and data dictionary for the downloaded PHMSA release. The importer validates mapped columns, parses selected date/numeric fields, preserves every original row as `raw_record`, and emits normalized JSON Lines. It does not assume that field names are identical across gas, liquid, LNG or historical files. The JSONL output is a staging artifact; database loading and source-release-specific validation remain separate steps.

## SEC-derived company financial analytics

The API exposes `GET /api/v1/energy/analytics/company/{ticker}`, which derives annual ratios from the issuer's SEC Company Facts observations. The dashboard requests this endpoint alongside the SEC fact table.

Calculated metrics include revenue growth, operating margin, net margin, free cash flow, free-cash-flow margin, operating-cash-flow/net-income cash conversion, return on assets, return on equity, long-term debt/assets, long-term debt/equity, net debt (only when both long-term debt and cash/equivalents are available), and capital-expenditure intensity.

Definitions and controls:
- Free cash flow = cash from operations minus the absolute value of reported PP&E acquisition cash outflow.
- ROA and ROE use period-end assets/equity, not average balances; they are screening ratios, not textbook average-balance returns.
- Leverage ratios currently use long-term debt concepts; they may omit current maturities and other financing liabilities.
- Cash conversion is null when net income is zero or unavailable.
- Revenue growth uses the nearest earlier reported annual period; fiscal year-end dates may differ by issuer.
- Missing source facts remain null. The service does not impute missing values.
- EBITDA, ROIC, enterprise value multiples, reserves, production and refinery utilization are not inferred from generic facts. They require further issuer-specific and operating-data ingestion.

The SEC's Company Facts API aggregates standardized taxonomy facts and does not include issuer-specific custom taxonomy tags. Those extensions may be required for comparable energy operating metrics. <https://www.sec.gov/search-filings/edgar-application-programming-interfaces>

## Data integrity and limitations
- No synthetic commodity prices or company financials are displayed.
- yfinance output is labeled historical market data with observation dates and provider disclaimers.
- EIA series have their own frequency, geography, units, revisions and facet codes. The catalog describes candidate endpoints; users must select valid EIA facets from current EIA metadata.
- The company universe is a curated starter list, not a complete global universe or claim that every company is a pure-play.
- Company financials and operating metrics should be populated from SEC XBRL/filings and official regulator datasets with source and period lineage.
- Pipeline and utility infrastructure maps are a later phase; respect PHMSA/FERC access and redistribution terms and avoid exposing sensitive operational details.
- Investment scores must be segment-specific and remain research signals subject to validation, costs and human review.
