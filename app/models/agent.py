from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import AgentStatus, AgentType, Country, NegotiationStyle, ProductType
from app.models import Base
from app.models.types import UTCDateTime, str_enum


class CollectionAgent(Base):
    __tablename__ = "agents"
    __table_args__ = (CheckConstraint("min_days_overdue >= 0", name="min_days_overdue_non_negative"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    agent_type: Mapped[AgentType] = mapped_column(str_enum(AgentType))
    country: Mapped[Country] = mapped_column(str_enum(Country))
    product_type: Mapped[ProductType] = mapped_column(str_enum(ProductType))
    negotiation_style: Mapped[NegotiationStyle] = mapped_column(str_enum(NegotiationStyle))
    min_days_overdue: Mapped[int]
    status: Mapped[AgentStatus] = mapped_column(
        str_enum(AgentStatus), default=AgentStatus.PAUSED, server_default=AgentStatus.PAUSED.value, index=True
    )
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(UTCDateTime, onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(UTCDateTime)
