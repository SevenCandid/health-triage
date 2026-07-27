# Deployment & Operations Manual

## 1. Overview & Architecture Setup

The system is deployed using containerized infrastructure with **Docker Compose** for local development/testing and orchestrated cloud containers (Kubernetes / AWS ECS) for production.

```mermaid
graph TD
    Client[PWA Static Assets - Vercel / Cloudfront S3] -->|HTTPS Requests| Nginx[Nginx Reverse Proxy / Load Balancer]
    Nginx -->|Proxy Pass gunicorn/uvicorn| API1[FastAPI Container 1]
    Nginx -->|Proxy Pass gunicorn/uvicorn| API2[FastAPI Container 2]
    API1 --> Postgres[(PostgreSQL 16 Database)]
    API2 --> Postgres
    API1 -.-> Gemini[Google Gemini API]
```

---

## 2. Docker Compose Configuration Blueprint (`docker-compose.yml`)

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: health_triage_db
    environment:
      POSTGRES_DB: health_triage
      POSTGRES_USER: triage_admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U triage_admin -d health_triage"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: health_triage_api
    environment:
      DATABASE_URL: postgresql+asyncpg://triage_admin:${DB_PASSWORD}@postgres:5432/health_triage
      GEMINI_API_KEY: ${GEMINI_API_KEY}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      ENVIRONMENT: production
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

volumes:
  postgres_data:
```

---

## 3. Production Server Stack (Gunicorn + Uvicorn)

- **ASGI Web Server**: Uvicorn worker class managed by Gunicorn process manager:
  ```bash
  gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
  ```
- **Reverse Proxy**: Nginx handling SSL/TLS termination, HTTP/2 multiplexing, static asset caching, and Gzip/Brotli compression.

---

## 4. CI/CD Pipeline Blueprint (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: CI/CD Production Pipeline

on:
  push:
    branches: [ main ]

jobs:
  test-and-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          
      - name: Install Backend Dependencies & Run Pytest
        run: |
          cd backend
          pip install -r requirements.txt
          pytest tests/
          
      - name: Set up Node.js 20
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          
      - name: Build & Test React PWA Frontend
        run: |
          cd frontend
          npm ci
          npm run test:unit
          npm run build
```
