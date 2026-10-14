import os

# Antes de importar la app: sin dispatcher en background y con una clave válida
os.environ.setdefault("SECRET_KEY", "test-secret-key-with-at-least-32-characters")
os.environ["DISPATCHER_ENABLED"] = "false"
os.environ["ENVIRONMENT"] = "test"

import itertools  # noqa: E402
from datetime import UTC, datetime, timedelta  # noqa: E402
from decimal import Decimal  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.api.deps import get_call_engine, get_clock  # noqa: E402
from app.auth import hash_password  # noqa: E402
from app.database import get_db  # noqa: E402
from app.domain.enums import CallOutcome, Country, ProductType  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base, Debtor, KlevaUser  # noqa: E402
from app.services.call_engine.base import AgentSnapshot, CallResult, DebtorSnapshot, TranscriptLine  # noqa: E402

# StaticPool: todas las sesiones comparten LA MISMA conexión.
# Sin él, cada conexión a ":memory:" abre una base nueva y vacía.
engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

USER_PASSWORD = "Password123"
AGENT_PAYLOAD = {
    "name": "Valeria",
    "agent_type": "financial",
    "country": "AR",
    "product_type": "credit_card",
    "negotiation_style": "soft",
    "min_days_overdue": 30,
}
_dni = itertools.count(30_000_000)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


async def _reset_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def _drop_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


class FrozenClock:
    """Reloj controlable: los tests avanzan el tiempo sin esperar."""

    def __init__(self, now: datetime):
        self.now = now

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **delta) -> None:
        self.now += timedelta(**delta)


class FixedOutcomeEngine:
    """Engine falso: devuelve el resultado que el test elige, para probar las reglas de persistencia."""

    name = "fixed"

    def __init__(self):
        self.outcome = CallOutcome.NO_ANSWER
        self.promised_days: int | None = None
        self.promised_amount: Decimal | None = None
        self.received: list[tuple[AgentSnapshot, DebtorSnapshot]] = []

    def set(self, outcome: CallOutcome, promised_days: int | None = None, promised_amount: str | None = None):
        self.outcome = outcome
        self.promised_days = promised_days
        self.promised_amount = Decimal(promised_amount) if promised_amount else None

    async def run(self, agent: AgentSnapshot, debtor: DebtorSnapshot) -> CallResult:
        self.received.append((agent, debtor))
        return CallResult(
            self.outcome,
            30,
            [TranscriptLine("system", "fixed")],
            self.name,
            self.promised_days,
            self.promised_amount,
        )


def make_debtor(**overrides) -> Debtor:
    data = {
        "first_name": "Juan",
        "last_name": "Pérez",
        "dni": str(next(_dni)),
        "country": Country.AR,
        "product_type": ProductType.CREDIT_CARD,
        "balance": Decimal("1000.00"),
        "days_overdue": 45,
    }
    data.update(overrides)
    return Debtor(**data)


@pytest.fixture
def clock() -> FrozenClock:
    return FrozenClock(datetime(2026, 10, 14, 12, 0, tzinfo=UTC))


@pytest.fixture
def call_engine() -> FixedOutcomeEngine:
    return FixedOutcomeEngine()


@pytest.fixture
def session_factory():
    return TestingSessionLocal


@pytest.fixture
def client(clock, call_engine):
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_clock] = lambda: clock
    app.dependency_overrides[get_call_engine] = lambda: call_engine
    with TestClient(app) as c:
        c.portal.call(_reset_schema)  # Clean + Setup, en el event loop del TestClient
        yield c
        c.portal.call(_drop_schema)
    app.dependency_overrides.clear()


@pytest.fixture
def db_add(client):
    """Inserta entidades directo en la base: no hay endpoints para crear usuarios ni deudores."""

    def _add(*objs):
        async def _insert():
            async with TestingSessionLocal() as session:
                session.add_all(objs)
                await session.commit()
                for obj in objs:
                    await session.refresh(obj)
            return list(objs)

        return client.portal.call(_insert)

    return _add


@pytest.fixture
def kleva_user(db_add) -> KlevaUser:
    [user] = db_add(
        KlevaUser(
            first_name="Ana",
            last_name="Kleva",
            email="ana@kleva.demo",
            password_hash=hash_password(USER_PASSWORD),
        )
    )
    return user


@pytest.fixture
def auth_headers(client, kleva_user) -> dict[str, str]:
    response = client.post("/api/auth/login", data={"username": kleva_user.email, "password": USER_PASSWORD})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def create_agent(client, auth_headers):
    def _create(**overrides) -> dict:
        response = client.post("/api/agents", json={**AGENT_PAYLOAD, **overrides}, headers=auth_headers)
        assert response.status_code == 201, response.text
        return response.json()

    return _create
