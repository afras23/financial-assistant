from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

async def pg_try_advisory_lock(session: AsyncSession, lock_key: int) -> bool:
    q = text("SELECT pg_try_advisory_xact_lock(:k)")
    res = await session.execute(q, {"k": lock_key})
    return bool(res.scalar() or False)
