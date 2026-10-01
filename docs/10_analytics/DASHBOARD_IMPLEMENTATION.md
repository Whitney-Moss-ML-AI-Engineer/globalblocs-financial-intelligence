# Dashboard Implementation

## Current implementation

The dashboard now has a defined API boundary between the presentation layer and financial-intelligence data layer.

```
Official Sources
    ↓
Bronze → Silver → Gold
    ↓
PostgreSQL / Parquet
    ↓
Analytics + ML/DL
    ↓
FastAPI /api/v1
    ↓
Dashboard
```

### API endpoints

- `GET /api/v1/health` — service and data-mode health.
- `GET /api/v1/domains` — the 12 GlobalBLOCS analytical domains.
- `GET /api/v1/overview` — dashboard KPI contract.
- `GET /api/v1/observations` — filterable observations.

The API currently returns **clearly labeled demo observations** so the dashboard can be developed without pretending that sample values are official live data.

## Production data contract

Replace the demo repository in `src/globalblocs/api/main.py` with a service/repository layer backed by validated Gold tables. Preserve:

- `source_id`
- `dataset_id`
- original `source_variable_name`
- canonical variable name
- entity/institution/instrument identifiers
- period
- observed value/text
- unit
- source record identifier
- source URL
- retrieval timestamp
- raw payload path
- transformation version

The API must expose provenance with analytical observations once Gold data is connected.

## Local development

```bash
pip install -e ".[dev]"
pip install "fastapi>=0.115" "uvicorn[standard]>=0.30"
PYTHONPATH=src uvicorn globalblocs.api.main:app --reload --port 8000
```

Open the existing dashboard at `dashboard/index.html`, then configure its API base URL to `http://127.0.0.1:8000` when API integration is enabled.

## Security requirements

Before production deployment:

1. Replace `allow_origins=["*"]` with the dashboard origin.
2. Add authentication and RBAC.
3. Store credentials only in environment/secrets management.
4. Add rate limiting and audit logging.
5. Validate all query parameters.
6. Never expose restricted SAR/CTR/FBAR data through public dashboard endpoints.
