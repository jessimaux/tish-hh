from fastapi import status
from httpx import AsyncClient


async def test_create_user(client: AsyncClient):
    request = {
        "email": "user@example.com",
        "username": "string",
        "password": "string"
    }
    response = await client.post('/users/registration/', json=request)
    assert response.status_code == status.HTTP_201_CREATED


async def test_get_me(auth_client: AsyncClient):
    response = await auth_client.get('/users/me/')
    assert response.status_code == status.HTTP_200_OK
