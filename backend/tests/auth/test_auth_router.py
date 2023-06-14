from fastapi import status
from fastapi.testclient import TestClient
from httpx import AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession
from apps.users.models import User



async def test_get_tokens(client: AsyncClient, user: User):
    request = {
        "username": "string",
        "password": "string"
    }
    response = await client.post('/auth/token/', data=request)
    assert response.status_code == status.HTTP_200_OK


async def test_refresh_tokens(client: AsyncClient, session: AsyncSession):
    pass
