from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class ExpenseCreate(BaseModel):
    user_id: UUID
    amount: float
    currency: str = Field(min_length=3, max_length=3)
    description: str
    idempotency_key: str

class ExpenseRead(BaseModel):
    id: UUID
    user_id: UUID
    amount: float
    currency: str
    description: str
    merchant: Optional[str] = None
    category: Optional[str] = None
