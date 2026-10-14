from datetime import datetime
from decimal import Decimal
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from app.domain.enums import (
    PRODUCT_CATEGORY,
    AgentStatus,
    AgentType,
    Country,
    NegotiationStyle,
    ProductType,
)

AgentName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=80)]
MinDays = Annotated[int, Field(ge=0, le=3650)]


def check_category(agent_type: AgentType, product_type: ProductType) -> None:
    if PRODUCT_CATEGORY[product_type] != agent_type:
        raise ValueError(f"El producto '{product_type}' no corresponde a un agente '{agent_type}'")


class AgentCreate(BaseModel):
    name: AgentName
    agent_type: AgentType
    country: Country
    product_type: ProductType
    negotiation_style: NegotiationStyle
    min_days_overdue: MinDays

    @model_validator(mode="after")
    def _product_matches_type(self) -> Self:
        check_category(self.agent_type, self.product_type)
        return self


class AgentUpdate(BaseModel):
    # La categoría se valida en el servicio, sobre el agente ya combinado con estos cambios
    name: AgentName | None = None
    agent_type: AgentType | None = None
    country: Country | None = None
    product_type: ProductType | None = None
    negotiation_style: NegotiationStyle | None = None
    min_days_overdue: MinDays | None = None


class AgentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    agent_type: AgentType
    country: Country
    product_type: ProductType
    negotiation_style: NegotiationStyle
    min_days_overdue: int
    status: AgentStatus
    created_at: datetime
    updated_at: datetime | None


class AgentStats(BaseModel):
    total: int
    no_answer: int
    payment_promise: int
    refused: int
    promised_amount_total: Decimal
