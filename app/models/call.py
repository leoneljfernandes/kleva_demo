from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import JSON, CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import CallOutcome
from app.models import Base
from app.models.types import UTCDateTime, str_enum


class Call(Base):
    __tablename__ = "calls"
    __table_args__ = (
        CheckConstraint(
            "(outcome = 'payment_promise') = (promised_days IS NOT NULL)", name="promise_fields_consistent"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id", ondelete="CASCADE"), index=True)
    debtor_id: Mapped[int] = mapped_column(ForeignKey("debtors.id", ondelete="CASCADE"), index=True)
    started_at: Mapped[datetime] = mapped_column(UTCDateTime, index=True)
    duration_seconds: Mapped[int]
    outcome: Mapped[CallOutcome] = mapped_column(str_enum(CallOutcome))
    promised_days: Mapped[int | None]
    promised_date: Mapped[date | None]
    promised_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    transcript: Mapped[list[dict]] = mapped_column(JSON, default=list)
    engine: Mapped[str] = mapped_column(String(30))  # qué implementación tomó la decisión

    agent: Mapped[CollectionAgent] = relationship(lazy="selectin")  # noqa: F821
    debtor: Mapped[Debtor] = relationship(lazy="selectin")  # noqa: F821
