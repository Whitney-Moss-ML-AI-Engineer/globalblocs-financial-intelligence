# GlobalBLOCS 25-Source ETL & EDA Framework

## Purpose
This module expands GlobalBLOCS into a global macroeconomic, financial, trade, energy, institutional, governance, inequality, and security data layer.

## Six analysis questions
| Type | Core question | Implementation |
|---|---|---|
| Descriptive | What happened? | Levels, rates, shares, distributions, country/year summaries |
| Exploratory | What's interesting? | Correlation, outliers, trends, clusters, regime changes |
| Inferential | What can we conclude? | Confidence intervals, t-tests, ANOVA, panel inference |
| Predictive | What will happen? | Time-ordered regression, ML, forecasting, scenarios |
| Causal | Why did it happen? | Fixed effects, lags, DiD/IV when justified |
| Mechanistic | How does it work? | Decomposition, structural equations, feedback/network mechanisms |

Causal routines are designs/tests, not automatic proof of causation.

## 25-source registry
1. World Bank World Development Indicators
2. IMF World Economic Outlook/DataMapper
3. WTO Statistics/API
4. UN Comtrade
5. OECD Data Explorer/SDMX
6. Bank for International Settlements Statistics
7. FRED
8. U.S. Treasury Fiscal Data
9. Federal Reserve Bank of New York Markets Data
10. U.S. Energy Information Administration
11. OPEC Annual Statistical Bulletin
12. International Energy Agency
13. European Central Bank Data Portal
14. Eurostat
15. Bank of England Database
16. Bank of Japan Time-Series Data
17. People's Bank of China
18. Reserve Bank of India DBIE
19. UNCTADstat
20. FAOSTAT
21. World Bank Worldwide Governance Indicators
22. V-Dem
23. Penn World Table
24. World Inequality Database
25. SIPRI Military Expenditure Database

## ETL contract
Every adapter preserves original source variables, units, frequencies, identifiers, dimensions, source URL, and retrieval timestamp. Silver transformations add canonical fields such as entity_name, period, value, unit, frequency, and country_code without deleting source columns. Gold tables contain derived indicators and model-ready features.

## Execution
Extract -> Bronze -> Validate -> Silver -> EDA -> Gold -> ML/DL -> Dashboard

Run:
python pipelines/ingestion/global_25_source_etl_eda.py

Sources requiring API keys, registration, or portal-selected downloads use environment variables and/or an official export URL. Never commit secrets.
