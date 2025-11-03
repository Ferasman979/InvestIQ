from datetime import datetime
from sqlite3 import IntegrityError
from sqlalchemy.orm import Session
from models.ledger import TransactionLedger
from models.Transcation import TransactionDB, TxStatus
from schemas.transaction import TransactionIn
#from provider.verification import Verificaiton

def create_transaction(db: Session, payload: TransactionIn) -> TransactionDB:
    tx = TransactionDB(
        amount=payload.amount,
        vendor=payload.vendor,
        category=payload.category,
        tx_date=payload.date,
        status=TxStatus.pending,
    )
    # if it goes to verification API we can have some liek tisd
    #verify_transaction(payload)
    # db.add(tx)
    # db.commit()
    # db.refresh(tx)
    return tx


def get_transaction(db: Session, tx_id: int) -> TransactionDB | None:
    return db.get(TransactionDB, tx_id)




def approve_transaction(db: Session, tx_id: int, provider_ref: str | None) -> tuple[TransactionDB, TransactionLedger | None]:
    tx = db.get(TransactionDB, tx_id)
    if not tx:
        return None, None

    # set status to approved
    tx.status = TxStatus.approved
    tx.updated_at = datetime.utcnow()
    db.add(tx)

    # write a permanent ledger record (idempotent via unique constraint)
    ledger = TransactionLedger(
        tx_id=tx.id,
        amount=tx.amount,
        vendor=tx.vendor,
        category=tx.category,
        tx_date=tx.tx_date,
        provider_ref=provider_ref,
    )
    db.add(ledger)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # already recorded — fetch existing
        ledger = db.query(TransactionLedger).filter(TransactionLedger.tx_id == tx.id).first()
        if not ledger:
            raise
    else:
        db.refresh(tx)
        db.refresh(ledger)

    return tx, ledger