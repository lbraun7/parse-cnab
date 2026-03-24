from fastapi import APIRouter
from app.api.v1.endpoints import auth, transactions

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(transactions.router)
