from collections.abc import Callable
from datetime import datetime
from typing import Annotated

from fastapi import Depends, Request

from app.clock import utcnow
from app.services.call_engine.base import CallEngine


def get_call_engine(request: Request) -> CallEngine:
    # Creado una sola vez en el lifespan: endpoint manual y dispatcher comparten el mismo rng
    return request.app.state.call_engine


def get_clock() -> Callable[[], datetime]:
    return utcnow


CallEngineDep = Annotated[CallEngine, Depends(get_call_engine)]
ClockDep = Annotated[Callable[[], datetime], Depends(get_clock)]
