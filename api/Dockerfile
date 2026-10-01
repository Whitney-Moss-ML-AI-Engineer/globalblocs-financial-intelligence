FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir "fastapi>=0.115" "uvicorn[standard]>=0.30" "pydantic>=2.0"
EXPOSE 8000
CMD ["uvicorn", "globalblocs.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
