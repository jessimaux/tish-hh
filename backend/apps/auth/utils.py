from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from jose import jwt

import settings
from apps.users.models import User


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str):
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str):
    return password_context.verify(password, hashed_pass)


def create_access_token(email: str, scopes: list[str] = [], expires_delta: int = None):
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow(
        ) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "email": email, "scopes": scopes}
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(email: str, expires_delta: int = None):
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow(
        ) + timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "email": str(email)}
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_REFRESH_SECRET_KEY, settings.JWT_ALGORITHM)
    return encoded_jwt


async def authenticate_user(session: AsyncSession, login: str, password: str):
    user = (await session.execute(select(User).where(User.email == login))).scalar()
    if not user:
        user = (await session.execute(select(User).where(User.username == login))).scalar()
        if not user:
            return False
    if not verify_password(password, user.password):
        return False
    return user
