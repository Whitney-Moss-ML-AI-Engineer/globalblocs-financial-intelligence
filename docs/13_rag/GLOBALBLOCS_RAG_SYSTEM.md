# GlobalBLOCS Retrieval-Augmented Generation (RAG) System

## Mission
Build an evidence-first research assistant that answers questions over official-source registries, macroeconomic and financial documentation, global market/regulatory models, ML algorithm catalogs, API/data contracts, and validated datasets. It supports research into economic regimes, company fundamentals, sector rotation, trade flows, financial risk, and potential investment opportunities without presenting generated text as financial truth.

## User experiences
- Web dashboard research workspace.
- Desktop app for Windows, macOS, and Linux using Tauri.
- Mobile app for iOS and Android using Expo/React Native.
- All clients call the same versioned FastAPI contract. No client embeds provider secrets or database credentials.

## Evidence flow
1. Resolve query and optional filters: jurisdiction, bloc, source family, period, sector, ticker.
2. Retrieve repository documents, source metadata, approved filings, and validated Gold-layer observations.
3. Rank passages and records; apply access controls before generation.
4. Build a context package containing source ID, title, URL/path, retrieval time, period, units, and quality status.
5. Generate an answer grounded in retrieved context; cite material claims.
6. Return uncertainty, missing-data status, conflicts, and evidence list.
7. Log query ID, source IDs, model/version, prompt-template version, and feedback without secrets.

## Retrieval tiers
- Tier 1: exact structured lookup for ticker, ISIN, jurisdiction, dataset, metric ID, and dates.
- Tier 2: lexical search using BM25/TF-IDF over documentation and filings.
- Tier 3: embedding/vector retrieval for semantic similarity.
- Tier 4: reranking and diversity controls to avoid over-representing one source.
- Use structured SQL and deterministic calculations for numeric answers. RAG must not invent official values from prose when queryable observations exist.

## Source hierarchy
1. National official source, regulator, or exchange where authoritative and available.
2. Official international organizations such as IMF, World Bank, BIS, WTO, UN Comtrade, OECD, and WFE for cross-country comparison and validation.
3. Licensed market-data providers and approved research sources, subject to contract.
4. Secondary commentary, explicitly labeled.
yfinance is a convenient research adapter for market/company series; it is not the authoritative filing source and does not replace exchange licensing or SEC/national regulator filings. Preserve ticker, retrieval timestamp, interval, adjustment policy, currency, timezone, and source limitations.

## 25 analytical global blocs / coverage groups
These are configurable analytical groupings, not a claim that there are 25 formal treaty organizations: North America; European Union; United Kingdom & Ireland; China; Japan; India; ASEAN; Australia & New Zealand; Latin America; Sub-Saharan Africa; Middle East & GCC; South Korea; Russia & CIS; Brazil; Mexico; South Africa; Türkiye; Switzerland; Nordic countries; Singapore; Indonesia; Malaysia; Hong Kong; Taiwan; and Global/Multilateral Markets. Countries may map to more than one group. Store many-to-many membership with effective dates rather than forcing a country into one bloc.

## Data domains
- Macroeconomics: GDP, prices, labor, production, consumption, housing, confidence, rates, yield curves.
- Equities and issuers: prices, volumes, corporate actions, financial statements, valuation, filings, ownership.
- Banking and credit: capital, liquidity, deposits, loans, NPLs, rates, spreads, debt securities.
- Trade and supply chains: reporter, partner, HS/SITC product, import/export flow, value, quantity, tariff and period.
- Sector intelligence: output, value added, employment, wages, productivity, capacity, energy, insolvencies.
- Policy/regulation: central-bank decisions, enforcement, sanctions, licensing, disclosures, trade actions.
- Transportation/logistics: shipping, ports, rail, air freight, trucking, border flows, and freight rates where available/licensed.
- Market sentiment and institutional products: volatility, positioning, funds, derivatives, structured finance where permitted.

## Machine-learning catalog
Expose the classical ML curriculum as a versioned registry: Naive Bayes, Logistic Regression, KNN, Random Forest classification/regression, SVM/SVR, Decision Trees classification/regression, simple and multiple linear regression, Lasso, K-Means, DBSCAN, PCA, ICA, FP-Growth, Apriori, Z-score, and Isolation Forest. Each model definition states task, assumptions, inputs, target, preprocessing, baseline, evaluation metrics, limitations, and intended use. Add deep-learning families as separately governed extensions.

## Investment-opportunity workflow
1. Define an investable universe and liquidity/market-cap constraints.
2. Join macro indicators, company fundamentals, prices/returns, sector data, trade exposure, and regulatory events by timestamp and entity.
3. Create point-in-time features; avoid look-ahead bias, survivorship bias, leakage, and restated-data leakage.
4. Establish a transparent baseline before complex ML.
5. Evaluate chronologically with rolling/expanding windows; never random-shuffle time-series data.
6. Classification: precision/recall, F1, ROC-AUC/PR-AUC, calibration, confusion matrix, class imbalance.
7. Regression: MAE, RMSE, R-squared, residual diagnostics, prediction intervals.
8. Clustering: silhouette, stability, and economic interpretability; association rules: support/confidence/lift; anomaly detection: precision at review capacity and false-positive cost.
9. Include transaction costs, spread, slippage, taxes where relevant, liquidity, drawdown, turnover, benchmark comparison, and out-of-sample testing.
10. Present candidates as research leads with rationale, contrary evidence, uncertainty, and risk flags—not personalized or guaranteed investment advice.

## Six analysis modes
- Descriptive: what happened?
- Exploratory: what patterns or anomalies may exist?
- Inferential: what can be inferred from a sample, with uncertainty?
- Predictive: what may happen out of sample?
- Causal: what changed because of an intervention, under explicit identification assumptions?
- Mechanistic: what plausible process could produce the observed outcome?

## Required evidence contract
Each answer should include answer text and limitations; citations with source IDs and stable URLs or repository paths; observation period, retrieval timestamp, units, and jurisdiction where applicable; data-quality and freshness status; whether official observations, yfinance, licensed data, documents, or model-generated interpretation were used; and an investment-research disclaimer when forecasts or opportunities are discussed.

## Security and governance
- Authentication and authorization at API, tenant, dataset, and document level.
- No credentials in prompts, logs, client bundles, or repository files.
- Treat retrieved documents as untrusted data, not instructions; resist prompt injection in filings and web pages.
- Restrict SAR/CTR/FBAR and other sensitive data to authorized access; never index restricted records into a general-purpose corpus.
- Apply source licensing, copyright, retention, and rate-limit requirements.
- Version chunker, embedding model, retrieval parameters, prompt, generator, and evaluation set.
- Monitor citation precision, groundedness, retrieval recall, latency, cost, stale-source rate, and abstention behavior.

## Delivery stages
1. Repository-document retrieval and citations.
2. Structured source registry and yfinance market-data adapters.
3. Vector retrieval plus hybrid reranking.
4. Optional hosted/local LLM generator behind a provider interface.
5. Dashboard research chat and evidence panel.
6. Tauri desktop and Expo mobile clients.
7. Evaluation harness, access controls, monitoring, signed releases.

## Current implementation boundary
The initial repository milestone should deliver source/data contracts, retrieval API, and UI integration seams. Clearly label demo or lexical retrieval; do not imply a production LLM/vector database is active until configured and tested.
