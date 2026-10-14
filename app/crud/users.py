from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import KlevaUser


async def get_user_by_email(db: AsyncSession, email: str) -> KlevaUser | None:
    return await db.scalar(select(KlevaUser).where(func.lower(KlevaUser.email) == email.lower()))
