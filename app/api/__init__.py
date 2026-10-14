from fastapi import APIRouter

from app.api import agents, auth, catalogs, debtors

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(catalogs.router, prefix="/catalogs", tags=["catalogs"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(debtors.router, prefix="/debtors", tags=["debtors"])
