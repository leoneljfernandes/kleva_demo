import asyncio
import logging
from collections.abc import Callable
from datetime import datetime

from opentelemetry import trace
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.crud import agents as crud_agents
from app.domain.enums import AgentStatus
from app.services.call_engine.base import CallEngine
from app.services.calls import place_call

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)  # no-op sin TracerProvider (tests, local)


class CallDispatcher:
    """Loop único: en cada tick, una llamada por agente activo, en secuencia.

    El estado vive en la DB: pausar es cambiar una columna y el loop lo ve en el próximo tick.
    Con commit por llamada, el segundo agente ya ve el next_contact_at que dejó el primero.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        engine: CallEngine,
        interval: float,
        clock: Callable[[], datetime],
    ):
        self.session_factory = session_factory
        self.engine = engine
        self.interval = interval
        self.clock = clock

    async def run_forever(self) -> None:
        logger.info("call dispatcher started (interval=%ss)", self.interval)
        while True:
            try:
                await self.tick()
            except Exception:
                logger.exception("dispatcher tick failed")  # un tick roto no mata el loop
            await asyncio.sleep(self.interval)

    async def tick(self) -> int:
        placed = 0
        async with self.session_factory() as db:
            for agent in await crud_agents.list_active(db):
                await db.refresh(agent)  # pudo pausarse mientras corría el tick
                if agent.status is not AgentStatus.ACTIVE or agent.deleted_at is not None:
                    continue
                # Un span por llamada: las queries quedan como hijos y el log de place_call lleva su trace_id
                with tracer.start_as_current_span("dispatcher.place_call", attributes={"agent.id": agent.id}):
                    if await place_call(db, agent, self.engine, self.clock()) is not None:
                        placed += 1
        return placed
