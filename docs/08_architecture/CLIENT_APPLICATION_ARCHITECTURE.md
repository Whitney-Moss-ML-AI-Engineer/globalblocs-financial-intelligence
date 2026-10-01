# GlobalBLOCS Client Application Architecture

## Objective
Provide one GlobalBLOCS platform through three client surfaces:
1. Web dashboard
2. Desktop application for Windows, macOS, and Linux
3. Mobile application for iOS and Android

All clients use the same versioned FastAPI service contract. The dashboard is never the system of record.

## Recommended production stack
- Web: HTML/CSS/JavaScript now; React/Next.js production target
- Desktop: Tauri 2
- Mobile: Expo/React Native
- API: Python + FastAPI + Pydantic
- Database: PostgreSQL
- Analytical storage: Parquet + object storage
- ETL: Python
- Analytics: pandas, NumPy, SciPy, statsmodels, scikit-learn
- ML/DL: PyTorch
- Containers: Docker + Docker Compose
- CI/CD: GitHub Actions
- Observability: structured logs, health endpoints, metrics
- Secrets: environment variables locally; managed secret store in production

## Installation model
### Desktop
The installer verifies OS, architecture, RAM/disk, network access, API endpoint, authentication, and optional Docker/local-service prerequisites.

### Mobile
The mobile application does not install PostgreSQL, Python, Docker, or ETL libraries on the phone. It connects to a secured HTTPS GlobalBLOCS API.

## Service profiles
- cloud: web/mobile/desktop connect to hosted API
- desktop-local: desktop connects to local API and PostgreSQL
- developer: full Python, Node, Docker, PostgreSQL, testing, ETL and ML/DL toolchain

## Security requirements
- HTTPS in production
- OAuth/OIDC or centralized authentication
- Short-lived access tokens
- No database credentials in frontend/mobile code
- Least-privilege database roles
- Restricted financial-crime data remains server-side and access-controlled
- Audit API and administrative actions
- Validate external-source ingestion before Gold-layer publication

## Repository layout
apps/desktop/
apps/mobile/
installer/
docs/08_architecture/CLIENT_APPLICATION_ARCHITECTURE.md
