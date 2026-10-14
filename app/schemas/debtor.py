from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.domain.enums import CallOutcome, Country, ProductType


class DebtorBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    dni: str


class DebtorResponse(DebtorBrief):
    country: Country
    product_type: ProductType
    balance: Decimal
    days_overdue: int
    next_contact_at: datetime | None
    last_call_outcome: CallOutcome | None
