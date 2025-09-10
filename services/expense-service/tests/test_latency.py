import asyncio, time, statistics
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_latency_p95_under_200ms():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        N = 120
        latencies = []
        async def hit():
            t0 = time.perf_counter()
            r = await ac.get("/health")
            assert r.status_code == 200
            latencies.append((time.perf_counter() - t0)*1000)
        await asyncio.gather(*[hit() for _ in range(N)])
        latencies.sort()
        p95 = latencies[int(len(latencies)*0.95)-1]
        assert p95 < 200, f"p95 was {p95:.2f}ms"
