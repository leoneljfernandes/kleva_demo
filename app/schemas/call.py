from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.domain.enums import CallOutcome
from app.schemas.debtor import DebtorBrief


class TranscriptLineSchema(BaseModel):
    speaker: Literal["system", "agent", "debtor"]
    text: str


class AgentBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class CallResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    agent: AgentBrief
    debtor: DebtorBrief
    started_at: datetime
    duration_seconds: int
    outcome: CallOutcome
    promised_days: int | None
    promised_date: date | None
    promised_amount: Decimal | None
    transcript: list[TranscriptLineSchema]
    engine: str
