from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.api.deps import CallEngineDep, ClockDep
from app.auth import CurrentUser
from app.crud import agents as crud_agents
from app.crud import calls as crud_calls
from app.database import DbSession
from app.domain.enums import AgentStatus
from app.schemas.agent import AgentCreate, AgentResponse, AgentStats, AgentUpdate
from app.schemas.call import CallResponse
from app.services import agents as agent_service
from app.services.calls import place_call

router = APIRouter()


@router.get("", response_model=list[AgentResponse])
async def list_agents(db: DbSession, _: CurrentUser):
    return await crud_agents.list_agents(db)


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(data: AgentCreate, db: DbSession, user: CurrentUser):
    return await agent_service.create_agent(db, data, user)


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: int, db: DbSession, _: CurrentUser):
    return await agent_service.get_agent(db, agent_id)


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: int, data: AgentUpdate, db: DbSession, _: CurrentUser):
    return await agent_service.update_agent(db, agent_id, data)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: int, db: DbSession, _: CurrentUser, clock: ClockDep):
    await agent_service.delete_agent(db, agent_id, clock())


@router.post("/{agent_id}/start", response_model=AgentResponse)
async def start_agent(agent_id: int, db: DbSession, _: CurrentUser):
    return await agent_service.set_status(db, agent_id, AgentStatus.ACTIVE)


@router.post("/{agent_id}/pause", response_model=AgentResponse)
async def pause_agent(agent_id: int, db: DbSession, _: CurrentUser):
    return await agent_service.set_status(db, agent_id, AgentStatus.PAUSED)


@router.post(
    "/{agent_id}/calls",
    response_model=CallResponse,
    status_code=status.HTTP_201_CREATED,
    responses={204: {"description": "No hay deudores elegibles para este agente"}},
)
async def call_now(agent_id: int, db: DbSession, _: CurrentUser, engine: CallEngineDep, clock: ClockDep):
    """Llamada manual: misma ruta de código que el dispatcher (place_call)."""
    agent = await agent_service.get_agent(db, agent_id)
    call = await place_call(db, agent, engine, clock())
    if call is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return call


@router.get("/{agent_id}/calls", response_model=list[CallResponse])
async def list_agent_calls(
    agent_id: int,
    db: DbSession,
    _: CurrentUser,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
):
    await agent_service.get_agent(db, agent_id)
    return await crud_calls.list_by_agent(db, agent_id, offset, limit)


@router.get("/{agent_id}/stats", response_model=AgentStats)
async def agent_stats(agent_id: int, db: DbSession, _: CurrentUser):
    await agent_service.get_agent(db, agent_id)
    return await crud_calls.stats_by_agent(db, agent_id)
