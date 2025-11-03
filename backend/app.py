from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.transaction_service import post_transaction
from services.notification_service import send_notification
import uuid

app = FastAPI(title="Guardian Verification Agent")

# CORS setup for frontend testing
from routers import transaction_router

app = FastAPI()
app.title = "guardian"

api = FastAPI(root_path="/api")
api.title = "guardian api"
app.mount("/api", api, name="api")


api.include_router(transaction_router.router, prefix="/transactions")
origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





@api.get("/healthcheck")
async def healthcheck():
    return {"status": "guardian is running"}

@api.get("/healthcheck")
async def api_healthcheck():
    return {"status": "guardian api is running"}


