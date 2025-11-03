import datetime as dt
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from models.Transcation import TxStatus

class TransactionIn(BaseModel):
    amount: Decimal = Field(gt=0, decimal_places=2, max_digits=12)
    vendor: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=80)
    date: dt.date

class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    amount: Decimal
    vendor: str
    category: str
    # this makes the response key be "tx_date" while we keep the field name "date"
    date: dt.date = Field(serialization_alias="tx_date")
    status: TxStatus
    created_at: dt.datetime
    updated_at: dt.datetime


class PostTransactionIn(BaseModel):
    approved: bool
    provider_ref: str | None = None

class PostTransactionOut(TransactionOut):
    ledger_id: int | None = None

class ApproveIn(BaseModel):
    provider_ref: str | None = None