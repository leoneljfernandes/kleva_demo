from collections.abc import Sequence
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import CallOutcome
from app.models import Call


def add(db: AsyncSession, call: Call) -> Call:
    """Agrega la llamada a la sesión SIN commit: place_call() confirma llamada + deudor juntos."""
    db.add(call)
    return call


async def get_call(db: AsyncSession, call_id: int) -> Call | None:
    return await db.get(Call, call_id)


async def list_by_agent(db: AsyncSession, agent_id: int, offset: int = 0, limit: int = 50) -> Sequence[Call]:
    result = await db.execute(
        select(Call)
        .where(Call.agent_id == agent_id)
        .order_by(Call.started_at.desc(), Call.id.desc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all()


async def list_by_debtor(
    db: AsyncSession, debtor_id: int, offset: int = 0, limit: int = 50
) -> Sequence[Call]:
    result = await db.execute(
        select(Call)
        .where(Call.debtor_id == debtor_id)
        .order_by(Call.started_at.desc(), Call.id.desc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all()


async def stats_by_agent(db: AsyncSession, agent_id: int) -> dict:
    rows = await db.execute(
        select(Call.outcome, func.count(), func.coalesce(func.sum(Call.promised_amount), 0))
        .where(Call.agent_id == agent_id)
        .group_by(Call.outcome)
    )
    counts = {outcome: 0 for outcome in CallOutcome}
    promised_total = Decimal("0")
    for outcome, count, amount in rows:
        counts[outcome] = count
        promised_total += Decimal(str(amount))
    return {
        "total": sum(counts.values()),
        "no_answer": counts[CallOutcome.NO_ANSWER],
        "payment_promise": counts[CallOutcome.PAYMENT_PROMISE],
        "refused": counts[CallOutcome.REFUSED],
        "promised_amount_total": promised_total.quantize(Decimal("0.01")),
    }
