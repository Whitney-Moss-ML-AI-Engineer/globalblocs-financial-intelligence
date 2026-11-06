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

## Data integrity and limitations
- No synthetic commodity prices or company financials are displayed.
- yfinance output is labeled historical market data with observation dates and provider disclaimers.
- EIA series have their own frequency, geography, units, revisions and facet codes. The catalog describes candidate endpoints; users must select valid EIA facets from current EIA metadata.
- The company universe is a curated starter list, not a complete global universe or claim that every company is a pure-play.
- Company financials and operating metrics should be populated from SEC XBRL/filings and official regulator datasets with source and period lineage.
- Pipeline and utility infrastructure maps are a later phase; respect PHMSA/FERC access and redistribution terms and avoid exposing sensitive operational details.
- Investment scores must be segment-specific and remain research signals subject to validation, costs and human review.
