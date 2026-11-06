# GlobalBLOCS Dashboard

The repository now includes a graphical dashboard at dashboard/index.html.

## User interface
- Overview: KPI cards, macro trend chart, intelligence summary, and data-quality status.
- Economics: economic-cycle and monetary-condition views plus an indicator table.
- Markets: market-condition and risk-monitoring views.
- ML / Deep Learning: algorithm selector, evaluation metrics, and analytics workflow.
- Data Explorer: searchable country/BLOC/variable observations.
- Export View: exports the active filter state as JSON.

## Production integration
The interface uses clearly labeled illustrative data for safe offline testing. Replace the sample adapter with validated Gold-layer data or an API service. Recommended production architecture: Official Sources → Bronze → Silver → Gold → Features → Statistics/Econometrics → ML/DL → Validation → Dashboard.

The dashboard should distinguish observed data, statistical estimates, predictive outputs, and scenarios. A model forecast or feature-importance value is not automatically causal evidence.


## Energy Intelligence
- Oil, Gas & Energy is a dedicated dashboard workspace covering commodity benchmarks, listed energy companies, upstream, services, midstream/pipelines, refining, gas utilities and electric utilities.
- API routes: /api/v1/energy/universe, /api/v1/energy/catalog, /api/v1/energy/market-data and /api/v1/energy/eia/query.
- EIA API access requires server-side EIA_API_KEY. yfinance is historical research data, not a licensed real-time feed.
- See docs/15_energy/ENERGY_INTELLIGENCE.md and docs/15_energy/ENERGY_DATA_MODEL.md.
