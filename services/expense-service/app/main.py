from fastapi import FastAPI
from .routers import expenses
from .db import init_models

app = FastAPI(title="Expense Service", version="1.0.0")

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(expenses.router)

@app.on_event("startup")
async def on_startup():
    await init_models()
