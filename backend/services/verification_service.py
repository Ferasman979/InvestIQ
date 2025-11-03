"""
Verification Service
Handles transaction verification flow including security questions
"""

from sqlalchemy.orm import Session
from models.Transcation import TransactionDB, TxStatus
from models.ledger import TransactionLedger
from providers.transactions import get_transaction, approve_transaction
from services.notification_service import send_notification
from services.detection_services import is_suspicious
from services.email_service import send_verification_email
from models.transaction_model import Transaction
from datetime import datetime
from logging_utils import get_logger

LOGGER = get_logger("guardian")


class SecurityQuestion:
    """Security question structure"""
    def __init__(self, question: str, answer: str):
        self.question = question
        self.answer = answer.lower().strip()


def verify_transaction(db: Session, tx_id: int, db_transaction: TransactionDB) -> tuple[bool, str]:
    """
    Verify a transaction for suspicious activity.
    Returns (is_suspicious: bool, reason: str)
    """
    # Convert TransactionDB to Transaction model for detection service
    transaction_model = Transaction(
        transaction_id=str(db_transaction.id),
        user_id="",  # TODO: Add user_id to TransactionDB model
        amount=float(db_transaction.amount),
        currency="USD",  # TODO: Add currency field
        merchant=db_transaction.vendor,
        transaction_date=datetime.combine(db_transaction.tx_date, datetime.min.time()),
        status=db_transaction.status.value,
        suspicious_flag=False
    )
    
    # Check for suspicious activity
    suspicious, reason = is_suspicious(transaction_model)
    
    return suspicious, reason


def lock_transaction_for_verification(db: Session, tx_id: int, reason: str) -> TransactionDB:
    """
    Lock a transaction pending user verification.
    Updates status to pending and sends notification.
    """
    tx = get_transaction(db, tx_id)
    if not tx:
        raise ValueError(f"Transaction {tx_id} not found")
    
    # Set status to pending (locked for verification)
    # Note: We could add a 'locked' status, but pending works for now
    tx.status = TxStatus.pending
    tx.updated_at = datetime.utcnow()
    
    # Save to database
    db.add(tx)
    db.commit()
    db.refresh(tx)
    
    # Send email notification
    user_email = get_user_email(db, tx)  # TODO: Implement user email lookup
    if user_email:
        send_verification_email(
            user_email=user_email,
            transaction=tx,
            reason=reason,
            verification_url=f"/api/transactions/verify/{tx_id}"
        )
    
    # Create in-app notification
    user_id = get_user_id(db, tx)  # TODO: Implement user ID lookup
    if user_id:
        send_notification(
            user_id=user_id,
            message=f"Transaction {tx_id} has been temporarily locked for verification. Reason: {reason}. Please verify through your email."
        )
    
    LOGGER.warning(f"Transaction {tx_id} locked for verification: {reason}")
    
    return tx


def verify_with_security_questions(
    db: Session, 
    tx_id: int, 
    answers: dict[str, str]
) -> tuple[bool, str]:
    """
    Verify transaction with security question answers.
    Returns (verified: bool, message: str)
    """
    tx = get_transaction(db, tx_id)
    if not tx:
        return False, "Transaction not found"
    
    if tx.status != TxStatus.pending:
        return False, f"Transaction is in {tx.status} status and cannot be verified"
    
    # Get security questions for this transaction/user
    questions = get_security_questions(db, tx)
    
    if not questions:
        return False, "No security questions configured"
    
    # Verify answers
    correct_count = 0
    for question, expected_answer in questions.items():
        user_answer = answers.get(question, "").lower().strip()
        if user_answer == expected_answer:
            correct_count += 1
    
    # Require all answers to be correct
    if correct_count == len(questions):
        # Verification successful - approve transaction
        tx.status = TxStatus.verified
        tx.updated_at = datetime.utcnow()
        db.add(tx)
        db.commit()
        db.refresh(tx)
        
        LOGGER.info(f"Transaction {tx_id} verified successfully")
        return True, "Transaction verified successfully"
    else:
        LOGGER.warning(f"Transaction {tx_id} verification failed: {correct_count}/{len(questions)} correct")
        return False, f"Verification failed: {correct_count}/{len(questions)} answers correct"


def get_security_questions(db: Session, tx: TransactionDB) -> dict[str, str]:
    """
    Get security questions for a transaction/user.
    Returns dict of {question: expected_answer}
    """
    # TODO: Implement actual security questions lookup from database
    # For now, return preset questions
    # In production, these should be user-specific and stored in database
    
    # Preset security questions (should be user-specific)
    questions = {
        "What is your mother's maiden name?": "smith",  # TODO: Get from user profile
        "What city were you born in?": "toronto",  # TODO: Get from user profile
        "What is your favorite pet's name?": "fluffy"  # TODO: Get from user profile
    }
    
    return questions


def get_user_email(db: Session, tx: TransactionDB) -> str | None:
    """
    Get user email for transaction.
    TODO: Implement actual user email lookup
    """
    # TODO: Add user_id to TransactionDB model and look up email
    # For now, return None or a placeholder
    return None  # or "user@example.com" for testing


def get_user_id(db: Session, tx: TransactionDB) -> str | None:
    """
    Get user ID for transaction.
    TODO: Implement actual user ID lookup
    """
    # TODO: Add user_id to TransactionDB model
    return None  # or "user123" for testing


def proceed_to_vendor(db: Session, tx_id: int, provider_ref: str | None = None) -> tuple[TransactionDB, TransactionLedger]:
    """
    After verification, proceed transaction to vendor and mark as completed.
    This calls approve_transaction which creates the ledger entry.
    """
    tx, ledger = approve_transaction(db, tx_id, provider_ref)
    
    if tx.status == TxStatus.approved:
        # Send confirmation notification
        user_id = get_user_id(db, tx)
        if user_id:
            send_notification(
                user_id=user_id,
                message=f"Transaction {tx_id} has been completed and sent to vendor {tx.vendor}"
            )
        
        LOGGER.info(f"Transaction {tx_id} completed and sent to vendor")
    
    return tx, ledger

