import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

EXPENSE_URL = os.getenv("EXPENSE_SERVICE_URL", "http://expense-service:8001")

app = FastAPI(title="API Gateway", version="1.1.0")

# Allow the frontend (5173) to call the gateway
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for demo; lock down in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/expenses")
async def list_expenses():
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.get(f"{EXPENSE_URL}/expenses")
        if r.status_code != 200:
            raise HTTPException(502, "Downstream error")
        return r.json()

@app.post("/expenses")
async def create_expense(payload: dict):
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.post(f"{EXPENSE_URL}/expenses", json=payload)
        if r.status_code != 200:
            raise HTTPException(r.status_code, r.text)
        return r.json()

@app.get("/insights/summary")
async def insights_summary(user_id: str):
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.get(f"{EXPENSE_URL}/expenses/stats/summary", params={"user_id": user_id})
        if r.status_code != 200:
            raise HTTPException(502, "Downstream error")
        return r.json()
