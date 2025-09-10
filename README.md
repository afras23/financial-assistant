# Machine Learning Financial Assistant for Personalised Budgeting

**Stack:** Python, FastAPI, Kafka, PostgreSQL, Docker, HuggingFace (optional), scikit-learn, React, Vite, TypeScript

This project is a microservices system for real-time expense parsing, budget categorisation, and personalised insights.
It demonstrates SWE best practices (CI, tests, structured configs), ML integration, and high concurrency targets
with optimistic concurrency control and distributed locking (PostgreSQL advisory locks).

---

## Quick Start

### Prerequisites
- Docker Desktop
- Node.js 20+ (if you want to run the frontend outside Docker)
- Python 3.11+ (optional, to run services locally)
- Internet access on first run (to pull docker images; ML may download model)

### 1) Clone & Boot
```bash
git clone <YOUR_REPO_URL> fin-assistant
cd fin-assistant
docker compose up --build -d
```

This will start:
- Zookeeper + Kafka
- Kafka UI at http://localhost:8085
- PostgreSQL at localhost:5432 (user: `postgres`, pass: `postgres`, db: `expenses`)
- Expense Service (FastAPI) at http://localhost:8001/docs
- ML Service (FastAPI + Kafka consumer) at http://localhost:8002/health
- API Gateway (FastAPI) at http://localhost:8000/docs
- Frontend (Vite React) at http://localhost:5173

### 2) Run DB Migrations
```bash
docker compose exec expense-service alembic upgrade head
```

### 3) Create Kafka Topics (idempotent)
```bash
docker compose exec kafka bash /app/create-topics.sh
```

### 4) Smoke Test
Create an expense (the ML service will enrich it asynchronously):
```bash
curl -X POST http://localhost:8001/expenses \
  -H "Content-Type: application/json" \
  -d '{"user_id":"00000000-0000-0000-0000-000000000001","amount":12.99,"currency":"GBP","description":"Latte at Starbucks","idempotency_key":"demo-1"}'
```

List expenses:
```bash
curl http://localhost:8001/expenses
```

Fetch insights via gateway:
```bash
curl http://localhost:8000/insights/summary?user_id=00000000-0000-0000-0000-000000000001
```

### 5) Run Tests (CI-like locally)
```bash
docker compose exec expense-service pytest -q
docker compose exec ml-service pytest -q
```

---

## Repo Layout

```
services/
  expense-service/
  ml-service/
  api-gateway/
frontend/
infra/
.github/workflows/ci.yml
docker-compose.yml
```

- **Expense Service**: REST for CRUD expenses, emits Kafka `expenses.raw`, uses advisory locks + optimistic versioning for monthly budgets.
- **ML Service**: Kafka consumer parses & classifies expenses (scikit-learn TF-IDF pipeline). Publishes to `expenses.parsed`.
- **API Gateway**: Aggregates APIs and provides insights endpoint consuming expense-service stats.
- **Frontend**: React dashboard calling the gateway.
- **Infra**: Kafka topic creation script.

---

## Concurrency Guarantees

- **Idempotency keys** on expense creation.
- **PostgreSQL advisory locks** for budget aggregation section.
- **Optimistic concurrency** on `budgets.version` with retry (compare-and-swap).
- **Integration test** fires 100 parallel `/health` requests and asserts p95 latency < 200ms on typical laptops.

---

## Environment

Default env is set via docker-compose:
- DB: `postgresql+asyncpg://postgres:postgres@postgres:5432/expenses`
- Kafka: `kafka:9092`
- Topics: `expenses.raw`, `expenses.parsed`, `insights.events`

---

## Notes

- The ML service ships with a tiny labeled dataset under `services/ml-service/data/`. It trains a light TF-IDF + LogisticRegression model on startup if `model.joblib` is absent.
- If HuggingFace model download fails, the service gracefully falls back to the TF-IDF pipeline only.

---

## Production-minded Extras
- CI with pytest + ruff + black
- Alembic migrations
- Health endpoints and readiness checks
- Typed Pydantic models
- Clean separation of concerns

Enjoy! 🎉
