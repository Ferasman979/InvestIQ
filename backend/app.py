from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import transaction_router
from logging_utils import get_logger

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

<<<<<<< HEAD




@api.get("/healthcheck")
=======
@app.get("/healthcheck")
>>>>>>> 2deddd95 (Chage App Name)
async def healthcheck():
    return {"status": "guardian is running"}

@api.get("/healthcheck")
async def api_healthcheck():
    return {"status": "guardian api is running"}


