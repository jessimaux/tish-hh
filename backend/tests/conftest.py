import sys
import os
import asyncio
from typing import AsyncGenerator, Generator

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import event, insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apps.auth.services import AuthService
from apps.users.repository import UserRepository
from apps.users.models import User

import settings
from database import Base, get_session
from main import app


SQLALCHEMY_DATABASE_TEST_URL = f"postgresql+asyncpg://{settings.DB_USER_TEST}:{settings.DB_PASSWORD_TEST}@{settings.DB_HOST_TEST}:{settings.DB_PORT_TEST}/{settings.DB_NAME_TEST}"
async_engine = create_async_engine(SQLALCHEMY_DATABASE_TEST_URL, poolclass=NullPool)
async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


USER_CREDENTIALS = {
    'email': 'sample@sample.com',
    'username': 'string',
    'password': 'string'
}


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session', autouse=True)
async def prepare_database() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='function')
async def session() -> AsyncGenerator[AsyncSession, None]:
    connection = await async_engine.connect()
    transaction = await connection.begin()
    session = async_session(bind=connection)
    # nested = await connection.begin_nested()

    # @event.listens_for(session.sync_session, "after_transaction_end")
    # def end_savepoint(session, transaction):
    #     nonlocal nested

    #     if not nested.is_active:
    #         nested = connection.sync_connection.begin_nested()

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()
    

@pytest.fixture(scope="function")
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    def override_get_session():
        yield session
    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def user(session: AsyncSession) -> User:
    return await UserRepository(session).create(email=USER_CREDENTIALS['email'],
                                                username=USER_CREDENTIALS['username'],
                                                password=AuthService(session).get_hashed_password(USER_CREDENTIALS['password']))


@pytest.fixture(scope="function")
async def auth_client(session: AsyncSession, user: User) -> AsyncGenerator[AsyncClient, None]:
    class DummyAuth:
        def __init__(self, username: str, password: str) -> None:
            self.username = username
            self.password = password

    def override_get_session():
        yield session
    app.dependency_overrides[get_session] = override_get_session

    tokens = await AuthService(session).get_tokens(DummyAuth(USER_CREDENTIALS['username'], USER_CREDENTIALS['password']))
    headers = {'Authorization': f'Bearer {tokens.access_token}'}
    async with AsyncClient(app=app, base_url="http://test", headers=headers) as ac:
        yield ac
