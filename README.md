# GlobalBLOCS Financial Intelligence Platform

**Institutional Macroeconomic & Financial Market Analysis Framework**

GlobalBLOCS is a systems-engineered financial intelligence platform designed to integrate official economic, financial, regulatory, and market data into reproducible analytics, machine learning, and AI-assisted research workflows.

## Mission

Build a transparent, auditable financial intelligence system that connects:

**Official Data Sources → Data Engineering → Features & Indicators → Statistical/ML Models → Risk Intelligence → AI-Assisted Research → Human Decision Support**

The platform is intended for research, portfolio development, quantitative analysis, financial risk analysis, and ML/AI engineering demonstration.

## Dashboard

A graphical end-user interface is now included at `dashboard/index.html`. It provides navigation for Overview, Economics, Markets, ML/Deep Learning, and Data Explorer workflows, with filters, KPI cards, trend charts, risk monitoring, model selection, and JSON export. The current UI uses clearly labeled illustrative data for offline interface testing; production integration should connect it to validated Gold-layer datasets or an API service.

See `dashboard/README.md` for the integration plan.

## Analytical Domains

1. Economic Cycle
2. Corporate Financial Health
3. Banking System
4. Institutional Investors
5. Credit Markets
6. Derivatives Markets
7. Structured Finance
8. Consumer Economy
9. Market Sentiment
10. International Finance
11. Monetary Policy
12. Risk & Compliance

## Systems Engineering Lifecycle

Mission Need → Stakeholders → Requirements → Architecture → Trade Studies → Design → Data Engineering → ML/AI Development → Integration → Verification → Validation → Deployment → Operations → Monitoring → Retirement

## Data Sources

The project prioritizes official/public sources including Federal Reserve/FRED, BEA, BLS, Census, SEC EDGAR/XBRL, FDIC, OCC, CFTC, FINRA, CFPB, U.S. Treasury, and PCAOB.

## Architecture

- **Bronze:** raw API responses, filings, CSV/JSON/XML/XBRL and source documents
- **Silver:** parsed, normalized, validated, deduplicated data
- **Gold:** analytical indicators, ratios, time series and engineered features
- **Intelligence:** statistical models, ML predictions, anomaly detection, regimes, risk measures and AI-assisted research

## Important Design Principle

LLMs are not treated as the source of truth. Deterministic official data and reproducible analytics remain authoritative; retrieval and AI layers operate on top of validated evidence.

## Status

**Phase 1 — Dashboard API Foundation + UI Integration**

The repository establishes systems-engineering documentation, requirements, architecture, source registry, Python package structure, testing strategy, development roadmap, and an end-user dashboard connected to a FastAPI service boundary. The API currently uses explicitly labeled demo observations; validated Gold-layer production data will replace the demo repository incrementally.

## Disclaimer

This project is an educational and engineering research platform. It is not investment, legal, accounting, tax, or regulatory advice. Model outputs are experimental unless explicitly validated and documented.

## License

MIT


## 12-Domain U.S. Financial Intelligence Expansion

The repository now includes an official-source architecture covering Economic Cycle, Corporate Financial Health, Banking System, Institutional Investors, Credit Markets, Derivatives Markets, Structured Finance, Consumer Economy, Market Sentiment, International Finance, Monetary Policy, and Risk & Compliance.

See `configs/us_official_data_sources.yaml` for the machine-readable source registry; `docs/07_database/RDBMS_OUTLINE.md` for the RDBMS curriculum/design standard; `docs/08_architecture/SOFTWARE_STACK.md` for the production stack; and `database/schema.sql` for the PostgreSQL reference schema.

Restricted financial-crime datasets such as SAR, CTR, and FBAR are explicitly classified as restricted rather than treated as public API sources.


## Dashboard Implementation

The dashboard now has a modular UI and FastAPI service boundary:

- `dashboard/index.html` — presentation shell
- `dashboard/styles.css` — responsive dashboard styling
- `dashboard/app.js` — API client, filters, state, and export
- `src/globalblocs/api/main.py` — FastAPI endpoints
- `docker-compose.yml` — local API container
- `docs/10_analytics/DASHBOARD_IMPLEMENTATION.md` — integration and security contract

Run locally with `pip install -e .` and `PYTHONPATH=src uvicorn globalblocs.api.main:app --reload --port 8000`. The dashboard falls back to clearly labeled demo mode when the API is unavailable.
