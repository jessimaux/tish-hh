from datetime import datetime, timedelta

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from jose import jwt, JWTError

import settings
from apps.users.repository import UserRepository
from .repository import *
from .schemas import *


USER_SCOPE = ['profile', 'users', 'categories', 'events', 'signs', 'tags', 'messages']


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.session_repository = SessionRepository(session)
        self.user_repository = UserRepository(session)
        self.password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_hashed_password(self, password: str):
        return self.password_context.hash(password)

    def verify_password(self, password: str, hashed_pass: str):
        return self.password_context.verify(password, hashed_pass)

    def _create_access_token(self, username: str, scopes: list[str] = [], expires_delta: int = None):
        if expires_delta is not None:
            expires_delta = datetime.utcnow() + expires_delta
        else:
            expires_delta = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode = {"exp": expires_delta, "username": username, "scopes": scopes}
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
        return encoded_jwt

    def _create_refresh_token(self, username: str, scopes: list[str] = [], expires_delta: int = None):
        if expires_delta is not None:
            expires_delta = datetime.utcnow() + expires_delta
        else:
            expires_delta = datetime.utcnow() + timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)

        to_encode = {"exp": expires_delta, "username": username, "scopes": scopes}
        encoded_jwt = jwt.encode(to_encode, settings.JWT_REFRESH_SECRET_KEY, settings.JWT_ALGORITHM)
        return encoded_jwt

    # TODO: rewrite method get_by_email_or_username, also check method
    async def _authenticate_user(self, login: str, password: str):
        user = await self.user_repository.get_by_username(login) or await self.user_repository.get_by_email(login)
        if not user:
            return False
        if not self.verify_password(password, user.password):
            return False
        return user

    # TODO: session under development
    async def get_tokens(self, user_form_data: OAuth2PasswordRequestForm) -> TokenPare:
        user = await self._authenticate_user(user_form_data.username, user_form_data.password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Incorrect username or password",)
        access_token = self._create_access_token(user.username, USER_SCOPE)
        refresh_token = self._create_refresh_token(user.username, USER_SCOPE)
        # client_session = await self.session_repository.create(user.id, refresh_token)
        return TokenPare(access_token=access_token, refresh_token=refresh_token)
    
    async def refresh_tokens(self, token: Token) -> TokenPare:
        try:
            payload = jwt.decode(token.token, settings.JWT_REFRESH_SECRET_KEY, settings.JWT_ALGORITHM)
        except JWTError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Could not validate token")
        user_obj = await self.user_repository.get_by_username(payload["username"])
        if not user_obj:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Incorrect username or password")

        access_token = self._create_access_token(user_obj.username, payload["scopes"])
        refresh_token = self._create_refresh_token(user_obj.username, payload["scopes"])

        client_session = await self.session_repository.get_by_user_and_rt(user_obj.id, token.token)
        if not client_session:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Session doesnt exist")
        client_session = await self.session_repository.update(client_session.id, refresh_token)
        return TokenPare(access_token=access_token, refresh_token=refresh_token)
