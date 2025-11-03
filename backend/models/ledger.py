from datetime import datetime
from sqlalchemy import Column, Integer, Numeric, String, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from db.db import Base

class TransactionLedger(Base):
    __tablename__ = "transaction_ledger"
    __table_args__ = (UniqueConstraint("tx_id", name="uq_ledger_tx_id"),)

    id = Column(Integer, primary_key=True, index=True)
    tx_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    vendor = Column(String(120), nullable=False)
    category = Column(String(80), nullable=False)
    tx_date = Column(Date, nullable=False)
    provider_ref = Column(String(120), nullable=True)   # external reference / payment id
    approved_at = Column(DateTime, default=datetime.utcnow, nullable=False) 
    transaction = relationship("TransactionDB", backref="ledger_entry")
