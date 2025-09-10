import asyncio
import os
from fastapi import FastAPI
import uvicorn
from .consumer import run_consumer

app = FastAPI(title="ML Service", version="1.0.0")

@app.get("/health")
async def health():
    return {"status": "ok"}

async def _bg():
    await run_consumer()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(_bg())
    uvicorn.run(app, host="0.0.0.0", port=8002)
