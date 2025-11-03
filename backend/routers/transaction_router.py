from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from services.notification_service import send_notification
from services.transaction_service import post_transaction
from services.detection_services import is_suspicious
from services.verification_service import (
    verify_transaction,
    lock_transaction_for_verification,
    verify_with_security_questions,
    proceed_to_vendor,
    get_security_questions
)
from db.db import get_db, SessionLocal
from schemas.transaction import ApproveIn, PostTransactionIn, PostTransactionOut, TransactionIn, TransactionOut
from schemas.verification import VerifyTransactionRequest, VerifyTransactionResponse, VerificationEmailResponse
from providers.transactions import approve_transaction, create_transaction, get_transaction
from models.Transcation import TxStatus
from logging_utils import get_logger
from models.transaction_model import Transaction

#name/backend
router = APIRouter()
LOGGER = get_logger("guardian")


@router.post("/create_trx", response_model=TransactionOut, status_code=201)
def create_tx(payload: TransactionIn, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Create a new transaction and automatically trigger verification.
    """
    # Create transaction
    tx = create_transaction(db, payload)
    
    # Save to database
    db.add(tx)
    db.commit()
    db.refresh(tx)
    
    # Automatically trigger verification in background
    background_tasks.add_task(verify_and_lock_if_suspicious, tx.id, db)
    
    LOGGER.info(f"Transaction {tx.id} created, verification triggered")
    
    # Return transaction with pending status (may be locked if suspicious)
    return TransactionOut(
        id=tx.id, amount=tx.amount, vendor=tx.vendor, category=tx.category,
        date=tx.tx_date, status=tx.status, created_at=tx.created_at, updated_at=tx.updated_at
    )


def verify_and_lock_if_suspicious(tx_id: int, db: Session):
    """
    Background task to verify transaction and lock if suspicious.
    """
    # Create new session for background task
    db_session = SessionLocal()
    try:
        tx = get_transaction(db_session, tx_id)
        if not tx:
            LOGGER.error(f"Transaction {tx_id} not found for verification")
            return
        
        # Verify transaction
        suspicious, reason = verify_transaction(db_session, tx_id, tx)
        
        if suspicious:
            # Lock transaction and send notifications
            lock_transaction_for_verification(db_session, tx_id, reason)
            LOGGER.warning(f"Transaction {tx_id} locked for verification: {reason}")
        else:
            # Transaction is not suspicious, can proceed normally
            # Status remains pending until explicitly approved
            LOGGER.info(f"Transaction {tx_id} passed verification checks")
            
    except Exception as e:
        LOGGER.error(f"Error in verification background task: {e}")
    finally:
        db_session.close()



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
    """
    Approve a transaction and send to vendor.
    Transaction must be in 'verified' or 'pending' status.
    """
    tx = get_transaction(db, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="transaction not found")
    
    # Check if transaction is in a valid state for approval
    if tx.status not in [TxStatus.pending, TxStatus.verified]:
        raise HTTPException(
            status_code=400,
            detail=f"Transaction is in {tx.status} status and cannot be approved"
        )

    # Proceed transaction to vendor (this marks it as approved and creates ledger)
    tx, ledger = proceed_to_vendor(db, tx_id, payload.provider_ref)

    return PostTransactionOut(
        id=tx.id, amount=tx.amount, vendor=tx.vendor, category=tx.category,
        date=tx.tx_date, status=tx.status, created_at=tx.created_at, updated_at=tx.updated_at,
        ledger_id=(ledger.id if ledger else None),
    )


@router.post("/verify/{tx_id}", response_model=VerifyTransactionResponse)
def verify_transaction_with_questions(
    tx_id: int,
    request: VerifyTransactionRequest,
    db: Session = Depends(get_db)
):
    """
    Verify a locked transaction using security questions.
    If verification succeeds, transaction status changes to 'verified' and can be approved.
    """
    tx = get_transaction(db, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="transaction not found")
    
    if tx.status != TxStatus.pending:
        raise HTTPException(
            status_code=400,
            detail=f"Transaction is in {tx.status} status and cannot be verified"
        )
    
    # Verify with security questions
    verified, message = verify_with_security_questions(db, tx_id, request.answers)
    
    if verified:
        # Transaction is now verified, can proceed to vendor
        return VerifyTransactionResponse(
            verified=True,
            message=message,
            transaction_id=tx_id,
            status=TxStatus.verified.value
        )
    else:
        return VerifyTransactionResponse(
            verified=False,
            message=message,
            transaction_id=tx_id,
            status=TxStatus.pending.value
        )


@router.get("/verify/{tx_id}/questions")
def get_verification_questions(tx_id: int, db: Session = Depends(get_db)):
    """
    Get security questions for a transaction that needs verification.
    """
    tx = get_transaction(db, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="transaction not found")
    
    if tx.status != TxStatus.pending:
        raise HTTPException(
            status_code=400,
            detail=f"Transaction is in {tx.status} status and does not require verification"
        )
    
    questions = get_security_questions(db, tx)
    
    return {
        "transaction_id": tx_id,
        "questions": list(questions.keys()),
        "message": "Please answer these security questions to verify the transaction"
    }



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