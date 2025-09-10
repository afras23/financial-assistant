from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from uuid import UUID
from datetime import datetime
import hashlib, os

from ..db import get_session
from .. import models, schemas
from ..lock import pg_try_advisory_lock
from aiokafka import AIOKafkaProducer

router = APIRouter(prefix="/expenses", tags=["expenses"])

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC_RAW = os.getenv("TOPIC_EXPENSES_RAW", "expenses.raw")

async def get_producer():
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP)
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()

@router.get("")
async def list_expenses(session: AsyncSession = Depends(get_session)):
    q = select(models.Expense).order_by(models.Expense.created_at.desc()).limit(100)
    rows = (await session.execute(q)).scalars().all()
    return [
        {
            "id": str(r.id),
            "user_id": str(r.user_id),
            "amount": float(r.amount),
            "currency": r.currency,
            "description": r.description,
            "merchant": r.merchant,
            "category": r.category,
        }
        for r in rows
    ]

@router.post("", response_model=schemas.ExpenseRead)
async def create_expense(
    body: schemas.ExpenseCreate,
    session: AsyncSession = Depends(get_session),
    producer: AIOKafkaProducer = Depends(get_producer),
):
    # Idempotency
    try:
        await session.execute(
            insert(models.IdempotencyKey).values(key=body.idempotency_key)
        )
    except Exception:
        # Already processed: fetch and return existing expense if present
        q = select(models.Expense).where(
            models.Expense.user_id == body.user_id,
            models.Expense.description == body.description,
            models.Expense.amount == body.amount,
            models.Expense.currency == body.currency,
        ).order_by(models.Expense.created_at.desc())
        row = (await session.execute(q)).scalar_one_or_none()
        if row:
            return {
                "id": row.id,
                "user_id": row.user_id,
                "amount": float(row.amount),
                "currency": row.currency,
                "description": row.description,
                "merchant": row.merchant,
                "category": row.category,
            }
        raise HTTPException(status_code=409, detail="Duplicate request")

    # Insert expense (merchant/category filled later by ML)
    result = await session.execute(
        insert(models.Expense)
        .values(
            user_id=body.user_id,
            amount=body.amount,
            currency=body.currency,
            description=body.description,
        )
        .returning(models.Expense)
    )
    expense = result.scalar_one()
    # Budget aggregation with advisory lock + optimistic concurrency
    month_yr = datetime.utcnow().strftime("%Y-%m")
    # Lock on hash(user_id+month_yr)
    lock_key = int(hashlib.sha256(f"{body.user_id}:{month_yr}".encode()).hexdigest(), 16) % (2**31)
    ok = await pg_try_advisory_lock(session, lock_key)
    if ok:
        # Upsert budget and CAS on version
        # Try to insert
        await session.execute(
            insert(models.Budget)
            .values(user_id=body.user_id, month_yr=month_yr, spent=0, version=1)
            .prefix_with("ON CONFLICT (user_id, month_yr) DO NOTHING")
        )
        # Read current
        current = await session.execute(
            select(models.Budget).where(
                models.Budget.user_id == body.user_id, models.Budget.month_yr == month_yr
            )
        )
        b = current.scalar_one()
        updated = await session.execute(
            update(models.Budget)
            .where(models.Budget.id == b.id, models.Budget.version == b.version)
            .values(spent=b.spent + body.amount, version=b.version + 1)
        )
        if updated.rowcount == 0:
            # lost CAS; a retry would happen by client or next request
            pass
    await session.commit()

    # Emit raw event
    event = {
        "id": str(expense.id),
        "user_id": str(expense.user_id),
        "amount": float(expense.amount),
        "currency": expense.currency,
        "description": expense.description,
        "created_at": datetime.utcnow().isoformat(),
    }
    await producer.send_and_wait(TOPIC_RAW, json.dumps(event).encode("utf-8"))

    return {
        "id": expense.id,
        "user_id": expense.user_id,
        "amount": float(expense.amount),
        "currency": expense.currency,
        "description": expense.description,
        "merchant": expense.merchant,
        "category": expense.category,
    }

@router.get("/stats/summary")
async def summary(user_id: UUID, session: AsyncSession = Depends(get_session)):
    # Aggregate last 30d
    from sqlalchemy import func
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    since = now - timedelta(days=30)
    q = (
        select(models.Expense.category, func.sum(models.Expense.amount))
        .where(models.Expense.user_id == user_id, models.Expense.created_at >= since)
        .group_by(models.Expense.category)
    )
    rows = (await session.execute(q)).all()
    return {"since": since.isoformat(), "totals": {k or "Uncategorised": float(v) for k, v in rows}}
