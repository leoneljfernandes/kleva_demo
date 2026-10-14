from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Nombres de constraints deterministas: Alembic los puede comparar y borrar
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


from app.models.agent import CollectionAgent  # noqa: E402,F401
from app.models.call import Call  # noqa: E402,F401
from app.models.debtor import Debtor  # noqa: E402,F401
from app.models.user import KlevaUser  # noqa: E402,F401
