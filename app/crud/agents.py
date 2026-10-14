from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import AgentStatus
from app.models import CollectionAgent


async def get_agent(db: AsyncSession, agent_id: int) -> CollectionAgent | None:
    """None también si el agente está borrado (soft delete)."""
    agent = await db.get(CollectionAgent, agent_id)
    if agent is None or agent.deleted_at is not None:
        return None
    return agent


async def list_agents(db: AsyncSession) -> Sequence[CollectionAgent]:
    result = await db.execute(
        select(CollectionAgent).where(CollectionAgent.deleted_at.is_(None)).order_by(CollectionAgent.id)
    )
    return result.scalars().all()


async def list_active(db: AsyncSession) -> Sequence[CollectionAgent]:
    result = await db.execute(
        select(CollectionAgent)
        .where(CollectionAgent.status == AgentStatus.ACTIVE, CollectionAgent.deleted_at.is_(None))
        .order_by(CollectionAgent.id)
    )
    return result.scalars().all()


async def create_agent(db: AsyncSession, agent: CollectionAgent) -> CollectionAgent:
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent


async def save(db: AsyncSession, agent: CollectionAgent) -> CollectionAgent:
    await db.commit()
    await db.refresh(agent)
    return agent
