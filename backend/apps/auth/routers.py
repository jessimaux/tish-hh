import datetime
import os
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, \
    File, UploadFile, BackgroundTasks, Security
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

import settings
from dependencies import get_session
from apps.users.models import User
from .schemas import *
from .utils import *
from .dependencies import *
from email_client import send_retrieve_password_link

# TODO:
# Complete jwt auth: at in coockie, rt localstorage
# Permission for register, refresh

router = APIRouter()


@router.post("/auth/token/", tags=['auth'], response_model=TokenPare)
async def login_for_access_token(response: Response,
                                 form_data: OAuth2PasswordRequestForm = Depends(),
                                 session: AsyncSession = Depends(get_session)):
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(user.email, scopes=form_data.scopes)
    refresh_token = create_refresh_token(user.email)

    response.set_cookie('access_token', access_token,
                        settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return TokenPare(access_token=access_token, refresh_token=refresh_token)


@router.post('/auth/refresh/', tags=['auth'], response_model=Token)
async def refresh_token(token: Token,
                        session: AsyncSession = Depends(get_session)):
    try:
        payload = jwt.decode(
            token.token, settings.JWT_REFRESH_SECRET_KEY, settings.JWT_ALGORITHM)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not validate token"
        )
    user_obj = (await session.execute(select(User).where(User.email == payload['email']))).scalar()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect username or password")
    access_token = create_access_token(user_obj.email)
    return Token(token=access_token)


