import logging
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.crud import calls as crud_calls
from app.crud import debtors as crud_debtors
from app.domain.enums import CallOutcome
from app.metrics import CALLS_TOTAL
from app.models import Call, CollectionAgent, Debtor
from app.services.call_engine.base import AgentSnapshot, CallEngine, CallResult, DebtorSnapshot

logger = logging.getLogger(__name__)


def next_contact_at(result: CallResult, now: datetime) -> datetime:
    match result.outcome:
        case CallOutcome.NO_ANSWER:
            return now + timedelta(minutes=settings.RETRY_NO_ANSWER_MINUTES)
        case CallOutcome.REFUSED:
            return now + timedelta(days=settings.REFUSED_COOLDOWN_DAYS)
        case CallOutcome.PAYMENT_PROMISE:
            # si no pagó al vencer la promesa (+ gracia), vuelve a la cola
            return now + timedelta(days=result.promised_days + settings.PROMISE_GRACE_DAYS)


def build_call(agent: CollectionAgent, debtor: Debtor, result: CallResult, started_at: datetime) -> Call:
    promised_date = (
        (started_at + timedelta(days=result.promised_days)).date()
        if result.promised_days is not None
        else None
    )
    return Call(
        agent=agent,
        debtor=debtor,
        started_at=started_at,
        duration_seconds=result.duration_seconds,
        outcome=result.outcome,
        promised_days=result.promised_days,
        promised_date=promised_date,
        promised_amount=result.promised_amount,
        transcript=[{"speaker": line.speaker, "text": line.text} for line in result.transcript],
        engine=result.engine,
    )


async def place_call(
    db: AsyncSession, agent: CollectionAgent, engine: CallEngine, now: datetime
) -> Call | None:
    """Única ruta para llamar: la usan el endpoint manual y el dispatcher."""
    debtor = await crud_debtors.next_eligible(db, agent, now)
    if debtor is None:
        return None
    result = await engine.run(AgentSnapshot.of(agent), DebtorSnapshot.of(debtor))
    call = crud_calls.add(db, build_call(agent, debtor, result, now))
    debtor.next_contact_at = next_contact_at(result, now)
    debtor.last_call_outcome = result.outcome
    await db.commit()  # llamada + actualización del deudor: una sola transacción
    CALLS_TOTAL.labels(result.outcome.value, agent.negotiation_style.value, agent.country.value).inc()
    logger.info("call placed agent_id=%s debtor_id=%s outcome=%s", agent.id, debtor.id, result.outcome.value)
    return call
