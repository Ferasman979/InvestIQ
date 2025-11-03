from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import transaction_router

app = FastAPI()
app.title = "guardian"

api = FastAPI(root_path="/api")
api.title = "guardian api"
app.mount("/api", api, name="api")


api.include_router(transaction_router.router, prefix="/transactions")
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


@api.get("/healthcheck")
async def healthcheck():
    """
    Endpoint to verify that the service is up and running
    """
    return {"status": "guardian is running"}