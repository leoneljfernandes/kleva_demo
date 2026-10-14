from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Index, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import CallOutcome, Country, ProductType
from app.models import Base
from app.models.types import UTCDateTime, str_enum


class Debtor(Base):
    __tablename__ = "debtors"
    __table_args__ = (
        UniqueConstraint("country", "dni", name="uq_debtors_country_dni"),
        Index("ix_debtors_eligibility", "country", "product_type", "days_overdue"),
        CheckConstraint("days_overdue >= 0", name="days_overdue_non_negative"),
        CheckConstraint("balance >= 0", name="balance_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(80))
    last_name: Mapped[str] = mapped_column(String(80))
    dni: Mapped[str] = mapped_column(String(20))
    country: Mapped[Country] = mapped_column(str_enum(Country))
    product_type: Mapped[ProductType] = mapped_column(str_enum(ProductType))
    balance: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    # Dato fijo del seed: no avanza con el tiempo (la emulación no lo necesita dinámico)
    days_overdue: Mapped[int]
    # Resume reintento, cooldown y promesa: NULL o pasado = elegible
    next_contact_at: Mapped[datetime | None] = mapped_column(UTCDateTime)
    last_call_outcome: Mapped[CallOutcome | None] = mapped_column(str_enum(CallOutcome))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, server_default=func.now())
