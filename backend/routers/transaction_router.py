from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from routers.llm_router import generate_security_question, verify_security_answer
from models.transaction_model import Transaction
from services.notification_service import send_notification
from services.transaction_service import post_transaction
from services.detection_services import is_suspicious
from db.db import get_db, SessionLocal
from schemas.transaction import ApproveIn, PostTransactionIn, PostTransactionOut, TransactionIn, TransactionOut
from providers.transactions import approve_transaction, create_transaction, get_transaction
from models.Transcation import TxStatus
from logging_utils import get_logger

#name/backend
router = APIRouter()
LOGGER = get_logger("guardian")
# Dummy in-memory database
TRANSACTIONS_DB = []

NOTIFICATIONS_DB = []


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
def approve_tx(tx_id: int, db: Session = Depends(get_db)):
    tx = get_transaction(db, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="transaction not found")
    
    return TransactionOut(
        id=tx.id,
        amount=tx.amount,
        vendor=tx.merchant,
        category=tx.category,
        date=tx.transaction_date,
        status=tx.status,
        created_at=tx.created_at,
        updated_at=tx.updated_at,
    )

@router.post("/api/verify-transaction-post-question")
async def get_question(transaction: Transaction):
    suspicious, reason = is_suspicious(transaction)
    if not suspicious:
        transaction.status = "approved"
        result = post_transaction(transaction)
        TRANSACTIONS_DB.append(result)
        LOGGER.info(f"Transaction approved: {transaction.transaction_id}")
        return {"transaction_id": transaction.transaction_id, "suspicious": False, "reason": "Normal"}
    if suspicious:
        transaction.status= "blocked"
        TRANSACTIONS_DB.append(transaction.dict())

        notif = send_notification(
        transaction.user_id,
        "I blocked the transaction because it seemed suspicious. Is it yours?"
        )
        NOTIFICATIONS_DB.append(notif)

        LOGGER.warning(f"Transaction blocked: {transaction.transaction_id} ({reason})")
        try:
            q_payload = generate_security_question()
            if isinstance(q_payload, JSONResponse):
                # error path from generate_security_question
                raise RuntimeError("Failed to generate security questions")
            security_questions = q_payload["security_questions"]
        except Exception as e:
            LOGGER.exception("Failed to generate security questions")
            raise HTTPException(
                status_code=500,
                detail="Unable to generate security questions",
            )
        return {
            "transaction_id": transaction.transaction_id,
            "suspicious": True,
            "reason": reason,
            "question": q_payload
        }





#Tauheed stuff below



@router.post("/api/verify-transaction")
async def verify_transaction(transaction: Transaction, answer:str):
    ans = verify_security_answer(answer)
    if ans:
        transaction.status = "approved"
        result = post_transaction(transaction)
        TRANSACTIONS_DB.append(result)
        LOGGER.info(f"Transaction approved: {transaction.transaction_id}")
        return {"transaction_id": transaction.transaction_id, "suspicious": False, "reason": "Normal"}
    
    transaction.status = "Failed"
    return {
        "transaction_id": transaction.transaction_id,
        "Transaction Status": transaction.status,
        "suspicious": True,
        "message": "Transaction failed"
        }
    # LOGGER.info(f"Received transaction: {transaction.transaction_id}")
    # suspicious, reason = is_suspicious(transaction)
        
    # # If not suspicious → approve and save
    # transaction.status = "approved"
    # result = post_transaction(transaction)
    # TRANSACTIONS_DB.append(result)
    # LOGGER.info(f"Transaction approved: {transaction.transaction_id}")
    # return {"transaction_id": transaction.transaction_id, "suspicious": False, "reason": "Normal"}




@router.get("/api/transactions")
async def get_transactions():
    """Get all transactions (simulated database)."""
    return {"transactions": TRANSACTIONS_DB}


@router.get("/api/notifications/{user_id}")
async def get_notifications(user_id: str):
    """Return all notifications for a user."""
    user_notifs = [n for n in NOTIFICATIONS_DB if n["user_id"] == user_id]
    return {"notifications": user_notifs}