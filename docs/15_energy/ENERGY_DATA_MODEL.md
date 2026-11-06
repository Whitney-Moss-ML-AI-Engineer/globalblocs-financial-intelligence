# Energy Data Model

Migration: database/migrations/004_energy_intelligence.sql

| Table | Purpose |
|---|---|
| energy.company | Listed company master and operating segment classification |
| energy.commodity | Commodity and benchmark definitions |
| energy.market_observation | Time-stamped prices with provider, source URL, unit and adjustment flag |
| energy.operating_observation | Company/asset operating metrics with periods and lineage |
| energy.infrastructure_asset | Refineries, pipelines, storage, processing and LNG infrastructure metadata |
| energy.regulatory_event | Pipeline/utility/company regulatory and safety events |

All observations retain source identifiers, source URLs, retrieval timestamps, period/unit metadata, and source-specific record IDs where available. Raw payloads belong in Bronze/object storage; normalized observations in Silver; validated ratios/features in Gold.
