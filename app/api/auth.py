from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import DUMMY_HASH, CurrentUser, create_access_token, verify_password
from app.crud.users import get_user_by_email
from app.database import DbSession
from app.schemas.auth import KlevaUserResponse, Token

router = APIRouter()

INCORRECT_LOGIN = HTTPException(
    status.HTTP_401_UNAUTHORIZED, "Incorrect email or password", headers={"WWW-Authenticate": "Bearer"}
)


@router.post("/login", response_model=Token)
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession):
    user = await get_user_by_email(db, form.username)
    if user is None:
        verify_password(form.password, DUMMY_HASH)  # mismo tiempo de respuesta exista o no
        raise INCORRECT_LOGIN
    valid, new_hash = verify_password(form.password, user.password_hash)
    if not valid or not user.is_active:
        raise INCORRECT_LOGIN
    if new_hash:  # hash heredado → re-hashear con Argon2
        user.password_hash = new_hash
        await db.commit()
    return Token(access_token=create_access_token(str(user.id)), token_type="bearer")


@router.get("/me", response_model=KlevaUserResponse)
async def me(user: CurrentUser):
    return user
