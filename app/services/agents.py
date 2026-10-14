from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import agents as crud_agents
from app.domain.enums import PRODUCT_CATEGORY, AgentStatus
from app.errors import ConflictError, NotFoundError, ValidationFailed
from app.models import CollectionAgent, KlevaUser
from app.schemas.agent import AgentCreate, AgentUpdate


class AgentIsActive(ConflictError):
    def __init__(self):
        super().__init__("El agente está activo: pausalo antes de editarlo o eliminarlo")


async def get_agent(db: AsyncSession, agent_id: int) -> CollectionAgent:
    agent = await crud_agents.get_agent(db, agent_id)
    if agent is None:
        raise NotFoundError("Agent not found")
    return agent


def _ensure_paused(agent: CollectionAgent) -> None:
    if agent.status is AgentStatus.ACTIVE:
        raise AgentIsActive()


async def create_agent(db: AsyncSession, data: AgentCreate, user: KlevaUser) -> CollectionAgent:
    agent = CollectionAgent(**data.model_dump(), status=AgentStatus.PAUSED, created_by=user.id)
    return await crud_agents.create_agent(db, agent)


async def update_agent(db: AsyncSession, agent_id: int, data: AgentUpdate) -> CollectionAgent:
    agent = await get_agent(db, agent_id)
    _ensure_paused(agent)
    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    agent_type = changes.get("agent_type", agent.agent_type)
    product_type = changes.get("product_type", agent.product_type)
    if PRODUCT_CATEGORY[product_type] != agent_type:
        raise ValidationFailed(f"El producto '{product_type}' no corresponde a un agente '{agent_type}'")
    for key, value in changes.items():
        setattr(agent, key, value)
    return await crud_agents.save(db, agent)


async def delete_agent(db: AsyncSession, agent_id: int, now: datetime) -> None:
    """Soft delete: preserva el historial de llamadas."""
    agent = await get_agent(db, agent_id)
    _ensure_paused(agent)
    agent.deleted_at = now
    await crud_agents.save(db, agent)


async def set_status(db: AsyncSession, agent_id: int, status: AgentStatus) -> CollectionAgent:
    """start/pause idempotentes: devuelven el agente aunque ya esté en ese estado."""
    agent = await get_agent(db, agent_id)
    if agent.status is not status:
        agent.status = status
        agent = await crud_agents.save(db, agent)
    return agent
