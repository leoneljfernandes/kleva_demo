"""Puerto de llamadas: el engine recibe snapshots inmutables y devuelve un CallResult.

No toca la DB. Hoy lo implementa SimulatedCallEngine; mañana un engine LLM con la misma firma.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal, Protocol, Self

from app.domain.enums import CallOutcome, Country, NegotiationStyle, ProductType
from app.models import CollectionAgent, Debtor


@dataclass(frozen=True)
class AgentSnapshot:
    id: int
    name: str
    country: Country
    negotiation_style: NegotiationStyle

    @classmethod
    def of(cls, agent: CollectionAgent) -> Self:
        return cls(agent.id, agent.name, agent.country, agent.negotiation_style)


@dataclass(frozen=True)
class DebtorSnapshot:
    id: int
    first_name: str
    country: Country
    product_type: ProductType
    balance: Decimal
    days_overdue: int

    @classmethod
    def of(cls, debtor: Debtor) -> Self:
        return cls(
            debtor.id,
            debtor.first_name,
            debtor.country,
            debtor.product_type,
            debtor.balance,
            debtor.days_overdue,
        )


@dataclass(frozen=True)
class TranscriptLine:
    speaker: Literal["system", "agent", "debtor"]
    text: str


@dataclass(frozen=True)
class CallResult:
    outcome: CallOutcome
    duration_seconds: int
    transcript: list[TranscriptLine]
    engine: str
    promised_days: int | None = None
    promised_amount: Decimal | None = None


class CallEngine(Protocol):
    name: str

    # async aunque la simulación no espere nada: un engine LLM sí va a esperar
    async def run(self, agent: AgentSnapshot, debtor: DebtorSnapshot) -> CallResult: ...
