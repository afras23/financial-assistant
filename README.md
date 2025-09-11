# 💸 Machine Learning Financial Assistant

[![CI](https://github.com/afras23/financial-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/afras23/financial-assistant/actions)

A microservices-based system for **personalized budgeting and expense categorization**.  
Built with **FastAPI, Kafka, PostgreSQL, Docker, React, and scikit-learn**.  

---

## 🚀 Features
- Real-time **expense parsing** and **budget categorization** using ML.
- **Microservices architecture**:
  - `expense-service`: Stores and manages expenses.
  - `ml-service`: Classifies expenses into categories.
  - `api-gateway`: Unified API access.
  - `frontend`: Simple React UI.
- **Kafka** for async communication.
- **PostgreSQL** persistence (local dev uses SQLite in CI).
- GitHub Actions **CI/CD** with unit tests on every service.

---

## 🏗 Architecture

```mermaid
flowchart LR
    UI[React Frontend] -->|HTTP| GW[API Gateway]
    GW --> EXP[Expense Service]
    GW --> ML[ML Service]
    EXP -->|Kafka| ML
    ML --> EXP
    EXP --> DB[(PostgreSQL)]
