"""Datos de ejemplo para desarrollo. Uso (con migraciones aplicadas): uv run python -m app.seed

Reproducible (semilla fija) e idempotente: se puede correr N veces sin duplicar.
"""

import asyncio
import random
from decimal import Decimal

from faker import Faker
from sqlalchemy import func, select

from app.auth import hash_password
from app.config import settings
from app.database import AsyncSessionLocal, engine
from app.domain.enums import PRODUCT_CATEGORY, AgentStatus, Country, NegotiationStyle, ProductType
from app.models import CollectionAgent, Debtor, KlevaUser

SEED = 42
SEED_PASSWORD = "Kleva2026"  # solo desarrollo; documentada en el README
DEBTORS_PER_COMBINATION = 8  # 8 países × 8 productos × 8 = 512 deudores: la demo no se queda sin elegibles
EXTRA_DEBTORS = 8

SEED_USERS = [
    {"first_name": "Admin", "last_name": "Kleva", "email": "admin@kleva.demo"},
]

SEED_AGENTS = [
    {
        "name": "Valeria",
        "country": Country.AR,
        "product_type": ProductType.CREDIT_CARD,
        "negotiation_style": NegotiationStyle.SOFT,
        "min_days_overdue": 30,
    },
    {
        "name": "Mateo",
        "country": Country.MX,
        "product_type": ProductType.INTERNET,
        "negotiation_style": NegotiationStyle.FLEXIBLE,
        "min_days_overdue": 15,
    },
    {
        "name": "Emily",
        "country": Country.US,
        "product_type": ProductType.ELECTRICITY,
        "negotiation_style": NegotiationStyle.STRICT,
        "min_days_overdue": 60,
    },
]

FAKER_LOCALE = {
    Country.AR: "es_AR",
    Country.CL: "es_CL",
    Country.CO: "es_CO",
    Country.MX: "es_MX",
    Country.US: "en_US",
    Country.VE: "es",
    Country.PE: "es",
    Country.PY: "es",
}

# Rango de deuda en USD por producto y tipo de cambio aproximado a moneda local (datos de demo)
USD_RANGE = {
    ProductType.CREDIT_CARD: (200, 5_000),
    ProductType.PERSONAL_LOAN: (500, 15_000),
    ProductType.MORTGAGE: (2_000, 40_000),
    ProductType.MOBILE_PHONE: (20, 300),
    ProductType.INTERNET: (30, 250),
    ProductType.ELECTRICITY: (40, 400),
    ProductType.WATER: (15, 150),
    ProductType.GAS: (20, 250),
}
USD_RATE = {
    Country.AR: 1_000,
    Country.CL: 900,
    Country.CO: 4_000,
    Country.MX: 18,
    Country.US: 1,
    Country.VE: 40,
    Country.PE: 3.7,
    Country.PY: 7_500,
}


def build_debtors(rng: random.Random) -> list[Debtor]:
    combos = [(c, p) for c in Country for p in ProductType] * DEBTORS_PER_COMBINATION
    combos += [(rng.choice(list(Country)), rng.choice(list(ProductType))) for _ in range(EXTRA_DEBTORS)]
    fakers = {country: Faker(locale) for country, locale in FAKER_LOCALE.items()}
    for fake in fakers.values():
        fake.seed_instance(SEED)

    used_dni: set[tuple[Country, str]] = set()
    debtors = []
    for country, product in combos:
        dni = str(rng.randint(10_000_000, 45_999_999))
        while (country, dni) in used_dni:
            dni = str(rng.randint(10_000_000, 45_999_999))
        used_dni.add((country, dni))
        low, high = USD_RANGE[product]
        balance = Decimal(str(rng.uniform(low, high) * USD_RATE[country])).quantize(Decimal("0.01"))
        fake = fakers[country]
        debtors.append(
            Debtor(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                dni=dni,
                country=country,
                product_type=product,
                balance=balance,
                days_overdue=rng.randint(1, 180),
            )
        )
    return debtors


async def seed() -> None:
    if settings.ENVIRONMENT == "production":
        raise SystemExit("El seed no corre en producción")
    rng = random.Random(SEED)

    async with AsyncSessionLocal() as session:
        admin_id = None
        for data in SEED_USERS:
            user = await session.scalar(select(KlevaUser).where(KlevaUser.email == data["email"]))
            if user:
                print(f"= usuario {data['email']} ya existe, se omite")
            else:
                user = KlevaUser(**data, password_hash=hash_password(SEED_PASSWORD))
                session.add(user)
                await session.flush()
                print(f"+ usuario {data['email']} creado")
            admin_id = admin_id or user.id

        if await session.scalar(select(func.count()).select_from(Debtor)):
            print("= deudores ya cargados, se omiten")
        else:
            debtors = build_debtors(rng)
            session.add_all(debtors)
            print(f"+ {len(debtors)} deudores creados")

        for data in SEED_AGENTS:
            query = select(CollectionAgent.id).where(CollectionAgent.name == data["name"])
            exists = await session.scalar(query)
            if exists:
                print(f"= agente {data['name']} ya existe, se omite")
                continue
            session.add(
                CollectionAgent(
                    **data,
                    agent_type=PRODUCT_CATEGORY[data["product_type"]],
                    status=AgentStatus.PAUSED,
                    created_by=admin_id,  # nada llama hasta que alguien lo active
                )
            )
            print(f"+ agente {data['name']} creado (pausado)")
        await session.commit()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
