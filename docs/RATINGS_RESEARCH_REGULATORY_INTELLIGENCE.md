# GlobalBLOCS Ratings, Research & Regulatory Intelligence

## Purpose

GlobalBLOCS now includes an institutional research layer covering:

- credit-rating agencies
- equity and investment research firms
- market-data and financial-intelligence providers
- bank research divisions
- ESG and sustainability providers
- risk and quantitative analytics firms
- U.S. financial regulatory reports
- derivatives, structured-finance, fixed-income and credit instruments

## Design principle

Provider data are treated as source observations, not as investment recommendations. GlobalBLOCS preserves the original provider, observation/action date, publication date, source document, methodology/version when available, and point-in-time availability.

Commercial providers such as S&P Global, Moody's, Fitch, Morningstar, Bloomberg, FactSet, MSCI and similar services require the applicable license, entitlement and current developer documentation. The application therefore uses configurable credentialed-request templates instead of hard-coding unverified commercial endpoints.

## Data architecture

Licensed/official source
→ source connector
→ Raw/Bronze
→ Silver/normalized
→ PostgreSQL metadata/core/analytics/compliance
→ Gold intelligence
→ 350 metrics
→ risk/credit/valuation/macro analysis
→ ML/deep learning
→ dashboard/API

## Point-in-time requirements

For research and machine learning, retain:

- provider
- entity identifier
- security identifier
- original rating/value
- rating or observation date
- publication date
- available-to-market date
- retrieval timestamp
- source document
- methodology/model version
- quality grade

Do not use later restatements, amended filings, or later rating actions in an earlier prediction window.

## Regulatory sources

The registry covers SEC, FDIC, Federal Reserve, OCC, FINRA, CFTC, NFA, CFPB, PCAOB and FinCEN. Restricted datasets are not treated as public ingestion targets. Ingestion must be limited to data the user is legally authorized to access and the applicable terms permit the system to use.

## 50-product catalog

The dashboard includes 50 products across:

1. Derivatives
2. Options
3. Futures & Forwards
4. Structured Finance
5. Fixed Income & Credit

These products are metadata/research catalog entries. Pricing, valuation and risk engines can be connected later to market-data and reference-data sources.

## Security

Never commit API keys, OAuth client secrets, JWTs or other credentials to GitHub. Use environment variables, Streamlit secrets, a production secret manager, or the appropriate enterprise credential store.
