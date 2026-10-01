# GlobalBLOCS Production Software Stack

## Four core layers

```
Presentation  → React/Next.js dashboard
Application   → FastAPI + Pydantic + auth/business logic
Data          → PostgreSQL + Parquet/object storage + cache
Infrastructure→ Docker + CI/CD + secrets + cloud/observability
```

## End-to-end architecture

```
Official APIs / bulk exports
          ↓
Source adapters
          ↓
Raw immutable landing
          ↓
Bronze — source-faithful
          ↓
Validation / lineage / quality
          ↓
Silver — canonical entities & measures
          ↓
Gold — analytical facts/features
          ↓
PostgreSQL + analytical views
          ↓
SQL / statistics / econometrics / ML / DL
          ↓
FastAPI services
          ↓
React/Next.js dashboard
```

## Recommended components

### Presentation
React/Next.js, TypeScript, accessible UI, interactive tables/charts, role-aware navigation.

### Application
FastAPI, Pydantic, REST endpoints, authentication/authorization, audit logging, request validation.

### ETL/data engineering
Python, pandas/Polars, Requests/httpx, source adapters, schema validation, Bronze/Silver/Gold transformations, Parquet.

### RDBMS
PostgreSQL, SQLAlchemy, Alembic, connection pooling, indexes, materialized views, row-level security where appropriate.

### Analytics
SQL, NumPy, pandas/Polars, SciPy, statsmodels, time-series analysis, econometrics, network analysis.

### ML/DL
scikit-learn, gradient boosting where approved, feature pipelines, model registry/monitoring, PyTorch for deep learning.

### AI/RAG
Document extraction, embeddings, retrieval, evidence-linked generation, source-aware prompts. Deterministic financial data remains authoritative over generated text.

### Infrastructure
Docker, GitHub Actions, environment configuration, secret management, structured logs, metrics, health checks, backups, disaster recovery.

## RDBMS versus object storage

PostgreSQL:
- source/dataset metadata
- entities/institutions/instruments
- filings and regulatory-event metadata
- normalized observations
- analytical dimensions/facts
- quality results
- lineage
- dashboard-serving views

Object storage/Parquet:
- raw API responses
- bulk files
- large filing extracts
- historical snapshots
- ML training datasets
- large intermediate analytical datasets

## Security

Never commit API keys. Classify public, controlled, confidential, and restricted data. Apply least privilege, encryption in transit/at rest, audit logging, retention rules, backups, and environment separation. Restricted SAR/CTR/FBAR information is not treated as publicly accessible.

## Production progression

Development → CI → container build → staging → data-quality validation → production → monitoring → scheduled ingestion → model refresh → dashboard/API release.
