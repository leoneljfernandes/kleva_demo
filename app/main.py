import asyncio
import random
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api import api_router
from app.clock import utcnow
from app.config import settings
from app.database import AsyncSessionLocal, engine
from app.errors import register_exception_handlers
from app.services.call_engine.simulated import SimulatedCallEngine
from app.services.dispatcher import CallDispatcher
from app.telemetry import setup_telemetry


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Un solo engine (y un solo rng) para el endpoint manual y el dispatcher
    app.state.call_engine = SimulatedCallEngine(random.Random(settings.SIMULATION_SEED), settings.ANSWER_RATE)
    task = None
    if settings.DISPATCHER_ENABLED:
        dispatcher = CallDispatcher(
            AsyncSessionLocal, app.state.call_engine, settings.DISPATCH_INTERVAL_SECONDS, utcnow
        )
        task = asyncio.create_task(dispatcher.run_forever())
    yield  # el esquema lo crean las migraciones, no create_all
    if task:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
    await engine.dispose()


app = FastAPI(title="Kleva Collections Demo", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # lista explícita, nunca "*" con credenciales
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
setup_telemetry(app, engine)
app.include_router(api_router, prefix="/api")


@app.get("/", include_in_schema=False)
async def root():
    return {"service": "kleva-collections", "docs": "/docs"}
