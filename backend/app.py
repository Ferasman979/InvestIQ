from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.transaction_service import post_transaction
from services.notification_service import send_notification
from services.detection_services import is_suspicious

app = FastAPI()
app.title = "Guardian Verification Agent"

api = FastAPI(root_path="/api")
api.title = "guardian api"
app.mount("/api", api, name="api")


# api.include_router(llm_router.router, prefix="/openai")
# api.include_router(auth_router.router, prefix="/auth")
# api.include_router(admin_router.router, prefix="/admin")
# api.include_router(pii_router.router, prefix="/pii")
# api.include_router(analytics_router.router, prefix="/data_leak")


# Allow Front-end Origin in local development
origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LOGGER = get_logger("guardian")

# Dummy in-memory database
TRANSACTIONS_DB = []

NOTIFICATIONS_DB = []


@app.get("/api/healthcheck")
async def healthcheck():
    return {"status": "guardian is running"}


@app.post("/api/verify-transaction")
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


@app.get("/api/transactions")
async def get_transactions():
    """Get all transactions (simulated database)."""
    return {"transactions": TRANSACTIONS_DB}

@app.get("/api/notifications/{user_id}")
async def get_notifications(user_id: str):
    """Return all notifications for a user."""
    user_notifs = [n for n in NOTIFICATIONS_DB if n["user_id"] == user_id]
    return {"notifications": user_notifs}