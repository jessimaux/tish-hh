import datetime

import settings
from apps.core.email import send_retrieve_password_link, send_verification_code
from apps.core.models import Session
from apps.users.crud import check_email, check_username
from apps.users.models import User
from apps.users.schemas import UserCreate
from dependencies import get_session
from fastapi import (APIRouter, BackgroundTasks, Depends, HTTPException,
                     Request, status)
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies import *
from .schemas import *
from .utils import *

router = APIRouter()


@router.post("/auth/token/", tags=["auth"], response_model=TokenPare)
async def login_for_access_token(request: Request,
                                 form_data: OAuth2PasswordRequestForm = Depends(),
                                 session: AsyncSession = Depends(get_session)):
    # # check for authorazation
    # if request.headers.get("Authorization"):
    #     raise HTTPException(status_code=403, detail="Already authenticated")

    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(user.username, scopes=USER_SCOPE)
    refresh_token = create_refresh_token(user.username, scopes=USER_SCOPE)

    client_session = Session(user_id=user.id, client=request.client.host, refresh_token=refresh_token)
    session.add(client_session)
    await session.commit()
    return TokenPare(access_token=access_token, refresh_token=refresh_token)


# TODO: delete session if jwt compromicated
@router.post("/auth/refresh/", tags=["auth"], response_model=TokenPare)
async def refresh_token(token: Token,
                        session: AsyncSession = Depends(get_session)):
    try:
        payload = jwt.decode(token.token, settings.JWT_REFRESH_SECRET_KEY, settings.JWT_ALGORITHM)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not validate token",
        )
    user_obj = (await session.execute(select(User)
                                      .where(User.username == payload["username"]))).scalar()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(user_obj.username, scopes=payload["scopes"])
    refresh_token = create_refresh_token(user_obj.username, scopes=payload["scopes"])
    # check for existing session
    client_session = (await session.execute(select(Session)
                                            .where(Session.user_id == user_obj.id,
                                                   Session.refresh_token == token.token))).scalar()
    if not client_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session doesnt exist",
        )
    client_session.refresh_token = refresh_token
    await session.commit()
    return TokenPare(access_token=access_token, refresh_token=refresh_token)


@router.post("/auth/registration/", tags=["auth"], response_model=UserRetrieve)
async def create_user(user: UserCreate,
                      request: Request,
                      background_tasks: BackgroundTasks,
                      session: AsyncSession = Depends(get_session)):
    if request.headers.get("Authorization"):
        raise HTTPException(status_code=403, detail="Already authenticated")
    if await check_email(user.email, session):
        raise HTTPException(status_code=400, detail="Email already registered")
    if await check_username(user.username, session):
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_hashed_password(user.password)
    user_obj = User(password=hashed_password, email=user.email, username=user.username)
    session.add(user_obj)
    await session.commit()

    # send activation email
    background_tasks.add_task(send_verification_code, user_obj, request, session)
    return user_obj


@router.post("/auth/send_retrieve_password/", tags=["auth"])
async def send_retrieve_password(password_retrieve_form: PasswordRetrieveBase,
                                 request: Request,
                                 background_tasks: BackgroundTasks,
                                 session: AsyncSession = Depends(get_session)):
    user_obj = (await session.execute(select(User)
                                      .where(User.email == password_retrieve_form.login))).scalar()
    if not user_obj:
        user_obj = (await session.execute(select(User)
                                          .where(User.username == password_retrieve_form.login))).scalar()
        if not user_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this credentials doesnt exists",
            )
    background_tasks.add_task(send_retrieve_password_link, user_obj, request)
    return JSONResponse(
        {"message": "Email to retrieve password sent"},
        status_code=status.HTTP_200_OK,
    )


@router.get("/auth/retrieve_password/{token}/", tags=["auth"])
async def retrieve_password(token: str,
                            session: AsyncSession = Depends(get_session)):
    """Method to get access for retrieve password page"""

    try:
        jwt_decoded = jwt.decode(token, settings.JWT_VERIFICATION_SECRET_KEY, settings.JWT_ALGORITHM)
        if datetime.datetime.fromtimestamp(jwt_decoded["exp"]) < datetime.datetime.now():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not validate token",
        )
    user_obj = (await session.execute(select(User)
                                      .where(User.username == jwt_decoded["username"]))).scalar()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid code or user doesn't exist",
        )
    return JSONResponse(
        {"message": "Verifed to change password"},
        status_code=status.HTTP_200_OK,
    )


@router.post("/auth/retrieve_password/{token}/", tags=["auth"])
async def retrieve_password(token: str,
                            pswrd_form: UserPasswordRetrieve,
                            session: AsyncSession = Depends(get_session)):
    try:
        jwt_decoded = jwt.decode(token, settings.JWT_VERIFICATION_SECRET_KEY, settings.JWT_ALGORITHM)
        if datetime.datetime.fromtimestamp(jwt_decoded["exp"]) < datetime.datetime.now():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not validate token",
        )
    user_obj = (await session.execute(select(User)
                                      .where(User.username == jwt_decoded["username"]))).scalar()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid code or user doesn't exist",
        )
    user_obj.password = get_hashed_password(pswrd_form.password)
    await session.commit()
    return JSONResponse(
        {"message": "Password changed successfully"},
        status_code=status.HTTP_200_OK,
    )


@router.get("/auth/verifyemail/{token}/", tags=["auth"])
async def verify_email(token: str,
                       session: AsyncSession = Depends(get_session)):
    try:
        jwt_decoded = jwt.decode(token, settings.JWT_VERIFICATION_SECRET_KEY, settings.JWT_ALGORITHM)
        if datetime.datetime.fromtimestamp(jwt_decoded["exp"]) < datetime.datetime.now():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not validate token",
        )
    user_obj = (await session.execute(select(User)
                                      .where(User.username == jwt_decoded["username"]))).scalar()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid code or user doesn't exist",
        )
    if user_obj.is_verifed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email can only be verified once",
        )
    user_obj.is_verifed = True
    await session.commit()
    return JSONResponse(
        {"message": "Account verified successfully"},
        status_code=status.HTTP_200_OK,
    )
