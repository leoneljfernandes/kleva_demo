from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.auth import CurrentUser
from app.crud import calls as crud_calls
from app.crud import debtors as crud_debtors
from app.database import DbSession
from app.domain.enums import Country, ProductType
from app.schemas.call import CallResponse
from app.schemas.debtor import DebtorResponse

router = APIRouter()


@router.get("", response_model=list[DebtorResponse])
async def list_debtors(
    db: DbSession,
    _: CurrentUser,
    country: Country | None = None,
    product_type: ProductType | None = None,
    min_days_overdue: Annotated[int | None, Query(ge=0)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
):
    return await crud_debtors.list_debtors(
        db,
        country=country,
        product_type=product_type,
        min_days_overdue=min_days_overdue,
        offset=offset,
        limit=limit,
    )


@router.get("/{debtor_id}", response_model=DebtorResponse)
async def get_debtor(debtor_id: int, db: DbSession, _: CurrentUser):
    debtor = await crud_debtors.get_debtor(db, debtor_id)
    if debtor is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Debtor not found")
    return debtor


@router.get("/{debtor_id}/calls", response_model=list[CallResponse])
async def list_debtor_calls(
    debtor_id: int,
    db: DbSession,
    _: CurrentUser,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
):
    if await crud_debtors.get_debtor(db, debtor_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Debtor not found")
    return await crud_calls.list_by_debtor(db, debtor_id, offset, limit)
