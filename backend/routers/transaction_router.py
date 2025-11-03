from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from services.notification_service import send_notification
from services.transaction_service import post_transaction
from services.detection_services import is_suspicious
from db.db import get_db, SessionLocal
from schemas.transaction import ApproveIn, PostTransactionIn, PostTransactionOut, TransactionIn, TransactionOut
from providers.transactions import approve_transaction, create_transaction, get_transaction
from models.Transcation import TxStatus
from logging_utils import get_logger
from models.transaction_model import Transaction

#name/backend
router = APIRouter()
LOGGER = get_logger("guardian")


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



#Tauheed stuff below

# Dummy in-memory database
TRANSACTIONS_DB = []

NOTIFICATIONS_DB = []

@router.post("/api/verify-transaction")
async def verify_transaction(transaction: Transaction):
    LOGGER.info(f"Received transaction: {transaction.transaction_id}")
    suspicious, reason = is_suspicious(transaction)

    if suspicious:
        transaction.status = "blocked"
        TRANSACTIONS_DB.append(transaction.dict())

        notif = send_notification(
        transaction.user_id,
        "I blocked the transaction because it seemed suspicious. Is it yours?"
        )
        NOTIFICATIONS_DB.append(notif)

        LOGGER.warning(f"Transaction blocked: {transaction.transaction_id} ({reason})")
        return {
            "transaction_id": transaction.transaction_id,
            "suspicious": True,
            "reason": reason,
        }

    # If not suspicious → approve and save
    transaction.status = "approved"
    result = post_transaction(transaction)
    TRANSACTIONS_DB.append(result)
    LOGGER.info(f"Transaction approved: {transaction.transaction_id}")
    return {"transaction_id": transaction.transaction_id, "suspicious": False, "reason": "Normal"}




@router.get("/api/transactions")
async def get_transactions():
    """Get all transactions (simulated database)."""
    return {"transactions": TRANSACTIONS_DB}


@router.get("/api/notifications/{user_id}")
async def get_notifications(user_id: str):
    """Return all notifications for a user."""
    user_notifs = [n for n in NOTIFICATIONS_DB if n["user_id"] == user_id]
    return {"notifications": user_notifs}