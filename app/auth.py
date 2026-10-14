from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

from app.config import settings
from app.database import DbSession
from app.models import KlevaUser

# Argon2id para hashes nuevos; bcrypt solo para verificar hashes heredados
password_hash = PasswordHash((Argon2Hasher(), BcryptHasher()))
DUMMY_HASH = password_hash.hash("dummy-password-for-timing")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

CREDENTIALS_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired token",
    headers={"WWW-Authenticate": "Bearer"},
)


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain: str, hashed: str) -> tuple[bool, str | None]:
    """Devuelve (válida, hash_nuevo). hash_nuevo != None → re-guardar (migra bcrypt → argon2)."""
    return password_hash.verify_and_update(plain, hashed)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    now = datetime.now(UTC)
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": subject, "iat": now, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY.get_secret_value(), algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY.get_secret_value(),
            algorithms=[settings.ALGORITHM],  # lista fija: evita ataques de "alg: none"
            options={"require": ["exp", "sub"]},
        )
    except jwt.InvalidTokenError:
        return None
    return payload["sub"]


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DbSession) -> KlevaUser:
    sub = decode_access_token(token)
    if sub is None or not sub.isdigit():
        raise CREDENTIALS_ERROR
    user = await db.get(KlevaUser, int(sub))
    if user is None or not user.is_active:
        raise CREDENTIALS_ERROR
    return user


CurrentUser = Annotated[KlevaUser, Depends(get_current_user)]
