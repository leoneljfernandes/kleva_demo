from fastapi import APIRouter

from app.auth import CurrentUser
from app.schemas.catalog import Catalogs
from app.services.catalogs import build_catalogs

router = APIRouter()


@router.get("", response_model=Catalogs)
async def get_catalogs(_: CurrentUser):
    return build_catalogs()
