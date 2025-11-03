from models.transaction_model import Transaction
from datetime import datetime

def post_transaction(transaction: Transaction):
    """
    Simulate saving a transaction (to DB or external API).
    """
    transaction.status = "approved"
    transaction.suspicious_flag = False
    transaction.updated_at = datetime.now()
    return transaction.dict()
