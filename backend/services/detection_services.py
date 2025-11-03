from models.transaction_model import Transaction

def is_suspicious(transaction: Transaction):
    """
    Simple rule-based anomaly detection.
    Returns (is_suspicious: bool, reason: str)
    """
    if transaction.amount > 5000:
        return True, "High transaction amount"

    if transaction.merchant.lower() in ["unknown_vendor", "fraud_shop", "test_merchant"]:
        return True, "Suspicious merchant"

    return False, "Transaction is normal"
