from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from db.db import get_db, SessionLocal
from schemas.transaction import ApproveIn, PostTransactionIn, PostTransactionOut, TransactionIn, TransactionOut
from providers.transactions import approve_transaction, create_transaction, get_transaction
from models.Transcation import TxStatus

#name/backend
router = APIRouter()


@router.post("/create_trx", response_model=TransactionOut, status_code=201)
def create_tx(payload: TransactionIn, db: Session = Depends(get_db)):
    tx = create_transaction(db, payload)
    #TO verify the transaction
    #verify_update_trx(tx.id, SessionLocal)
    # Manual mapping so the "date" field outputs as "tx_date"
    return TransactionOut(
        id=tx.id, amount=tx.amount, vendor=tx.vendor, category=tx.category,
        date=tx.tx_date, status=tx.status, created_at=tx.created_at, updated_at=tx.updated_at
    )



@router.get("/get_trx/{tx_id}", response_model=TransactionOut)
def get_tx(tx_id: int, db: Session = Depends(get_db)):
    tx = get_transaction(db, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="transaction not found")
    return TransactionOut(
        id=tx.id, amount=tx.amount, vendor=tx.vendor, category=tx.category,
        date=tx.tx_date, status=tx.status, created_at=tx.created_at, updated_at=tx.updated_at
    )



@router.post("/approve_trx/{tx_id}", response_model=PostTransactionOut)
def approve_tx(tx_id: int, payload: ApproveIn, db: Session = Depends(get_db)):
    tx = get_transaction(db, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="transaction not found")

    tx, ledger = approve_transaction(db, tx_id, payload.provider_ref)

    return PostTransactionOut(
        id=tx.id, amount=tx.amount, vendor=tx.vendor, category=tx.category,
        date=tx.tx_date, status=tx.status, created_at=tx.created_at, updated_at=tx.updated_at,
        ledger_id=(ledger.id if ledger else None),
    )