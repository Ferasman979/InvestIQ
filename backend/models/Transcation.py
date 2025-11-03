from datetime import datetime, date
from enum import Enum

from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, Enum as SAEnum
from db.db import Base


class TxStatus(str, Enum):
    pending = "pending"
    verified = "verified"
    failed = "failed"
    approved = "approved"


class TransactionDB(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    vendor = Column(String(120), nullable=False)
    category = Column(String(80), nullable=False)
    tx_date = Column(Date, nullable=False)
    status = Column(SAEnum(TxStatus), default=TxStatus.pending, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)