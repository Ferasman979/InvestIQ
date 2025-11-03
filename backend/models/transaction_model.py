from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    amount: float
    currency: str
    merchant: str
    transaction_date: datetime
    status: Optional[str] = "pending"
    suspicious_flag: Optional[bool] = False
    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()