from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import Country, ProductType
from app.models import CollectionAgent, Debtor


async def get_debtor(db: AsyncSession, debtor_id: int) -> Debtor | None:
    return await db.get(Debtor, debtor_id)


async def list_debtors(
    db: AsyncSession,
    *,
    country: Country | None = None,
    product_type: ProductType | None = None,
    min_days_overdue: int | None = None,
    offset: int = 0,
    limit: int = 50,
) -> Sequence[Debtor]:
    query = select(Debtor)
    if country is not None:
        query = query.where(Debtor.country == country)
    if product_type is not None:
        query = query.where(Debtor.product_type == product_type)
    if min_days_overdue is not None:
        query = query.where(Debtor.days_overdue >= min_days_overdue)
    query = query.order_by(Debtor.days_overdue.desc(), Debtor.id).offset(offset).limit(limit)
    return (await db.execute(query)).scalars().all()


async def next_eligible(db: AsyncSession, agent: CollectionAgent, now: datetime) -> Debtor | None:
    """Deudor a llamar: coincide con la config del agente y no está en reintento/cooldown/promesa.

    Prioriza la deuda más vieja y, a igual atraso, la más grande.
    """
    return await db.scalar(
        select(Debtor)
        .where(
            Debtor.country == agent.country,
            Debtor.product_type == agent.product_type,
            Debtor.days_overdue >= agent.min_days_overdue,
            or_(Debtor.next_contact_at.is_(None), Debtor.next_contact_at <= now),
        )
        .order_by(Debtor.days_overdue.desc(), Debtor.balance.desc(), Debtor.id)
        .limit(1)
    )
