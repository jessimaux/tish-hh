
from database import get_session
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies import *
from .schemas import *
from .services import *

auth_router = APIRouter()


@auth_router.post("/auth/token/", tags=["auth"], response_model=TokenPare)
async def get_tokens(user_form_data: OAuth2PasswordRequestForm = Depends(),
                     session: AsyncSession = Depends(get_session)):
    return await AuthService(session).get_tokens(user_form_data)


# TODO: delete session if jwt compromicated
#       check session work
@auth_router.post("/auth/refresh/", tags=["auth"], response_model=TokenPare)
async def refresh_tokens(token: Token,
                         session: AsyncSession = Depends(get_session)):
    return await AuthService(session).refresh_tokens(token)
