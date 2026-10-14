from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum
from sqlalchemy.types import TypeDecorator


class UTCDateTime(TypeDecorator):
    """timestamptz que siempre devuelve datetimes aware en UTC.

    Postgres ya lo hace; SQLite (tests) guarda sin zona y devolvería naive.
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect):
        if value is not None and value.tzinfo is not None:
            value = value.astimezone(UTC)
            if dialect.name == "sqlite":  # SQLite compara strings: todo en UTC naive
                value = value.replace(tzinfo=None)
        return value

    def process_result_value(self, value: datetime | None, dialect):
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value


def str_enum(enum_cls: type[StrEnum]) -> Enum:
    """VARCHAR + valor del enum ("credit_card", no "CREDIT_CARD").

    native_enum=False: agregar un valor no exige ALTER TYPE y funciona igual en SQLite.
    """
    return Enum(
        enum_cls,
        native_enum=False,
        length=32,
        values_callable=lambda e: [m.value for m in e],
        validate_strings=True,
    )
