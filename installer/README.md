# GlobalBLOCS Installation Wizard

The installation wizard is the first-run configuration interface for GlobalBLOCS.

## Modes
### Cloud / API mode
Recommended for normal end users. Required: a supported browser or GlobalBLOCS client and HTTPS access to the GlobalBLOCS API. No local PostgreSQL, Python, Docker, or ML stack is required.

### Desktop local mode
For analysts who want local services:
- Git
- Python 3.12+
- Docker Desktop
- PostgreSQL through Docker Compose
- Node.js 20+ when rebuilding the frontend

### Developer mode
Full engineering stack:
- Git
- Python 3.12+
- virtual environment
- FastAPI/Uvicorn
- Pydantic
- PostgreSQL
- Docker/Docker Compose
- Node.js 20+
- npm
- pandas, NumPy, SciPy, statsmodels, scikit-learn
- PyTorch
- Jupyter
- pytest, Ruff, mypy
- optional cloud/Terraform tooling

## Important
The wizard performs prerequisite checks and generates configuration instructions. It does not put secrets in source code and does not treat mobile devices as database hosts.

## Future releases
Desktop releases should be signed Tauri installers. Mobile releases should be signed iOS and Android builds.
