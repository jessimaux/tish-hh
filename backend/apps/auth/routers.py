import datetime
import os
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, File, UploadFile, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from dependencies import get_session
import settings
from .models import *
from .schemas import *
from .utils import *
from .dependencies import *
from email_client import send_verification_code, send_retrieve_password_link
from utils import handle_file_upload
from . import crud

# TODO:
# Complete jwt auth: at in coockie, rt localstorage
# Permission for register, refresh

router = APIRouter()


@router.post("/auth/reg/", tags=['auth'], response_model=UserRetrieve)
async def create_user(user: UserCreate,
                      request: Request,
                      background_tasks: BackgroundTasks,
                      session: AsyncSession = Depends(get_session)):
    if crud.check_email:
        raise HTTPException(
            status_code=400, detail="Email already registered")
    if crud.check_username:
        raise HTTPException(
            status_code=400, detail="Username already registered")
    hashed_password = get_hashed_password(user.password)
    user_obj = User(password=hashed_password,
                    email=user.email, username=user.username,
                    events=[], links=[])
    session.add(user_obj)
    await session.commit()

    background_tasks.add_task(send_verification_code,
                              user_obj, request, session)
    return user_obj


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
    access_token = create_access_token(user.email)
    refresh_token = create_refresh_token(user.email)

    response.set_cookie('access_token', access_token,
                        settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return TokenPare(access_token=access_token, refresh_token=refresh_token)


@router.get('/auth/refresh/', tags=['auth'])
async def refresh_token(token: Token,
                        request: Request,
                        response: Response,
                        session: AsyncSession = Depends(get_session)):
    try:
        payload = jwt.decode(
            token, settings.JWT_REFRESH_SECRET_KEY, settings.JWT_ALGORITHM)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not validate token"
        )
    user_res = await session.execute(select(User).where(User.email == payload['email']))
    user_obj = user_res.scalar()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect username or password")
    access_token = create_access_token(user_obj.email)
    return Token(access_token)


@router.get("/users/me/", tags=['users-me'], response_model=UserRetrieve)
def get_user_me(current_user: UserRetrieve = Depends(get_current_active_user)):
    return current_user


@router.post('/users/me/update/', tags=['users-me'], response_model=UserRetrieve)
async def update_user(user: UserUpdate,
                      current_user: UserRetrieve = Depends(
                          get_current_active_user),
                      session: AsyncSession = Depends(get_session)):
    current_user = await crud.update_user(user, current_user, session)
    return current_user


@router.post('/users/me/photo/', tags=['users-me'])
async def update_photo(file: UploadFile,
                       current_user: UserRetrieve = Depends(
                           get_current_active_user),
                       session: AsyncSession = Depends(get_session)):
    old_file = current_user.image
    try:
        current_user.image = await handle_file_upload(file, 'auth/profile/', ['image/jpeg', 'image/png'])
    finally:
        file_path = os.path.join(settings.BASEDIR, old_file[1:])
        if os.path.exists(file_path):
            os.remove(file_path)
    await session.commit()
    return current_user.image


@router.post('/users/me/change_password/', tags=['users-me'])
async def change_password(password_form: UserPasswordChange,
                          current_user: UserRetrieve = Depends(
                              get_current_active_user),
                          session: AsyncSession = Depends(get_session)):
    # verificate password
    if verify_password(password_form.old_password, current_user.password):
        # change password with hash, upd user
        current_user.password = get_hashed_password(password_form.new_password)
        await session.commit()
        return JSONResponse({"message": "Password changed successfully"}, status_code=status.HTTP_202_ACCEPTED)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incorrect old password"
        )


@router.post('/auth/send_retrieve_password/', tags=['auth'])
async def send_retrieve_password(pswrd_retrieve_form: PasswordRetrieveBase,
                                 request: Request,
                                 background_tasks: BackgroundTasks,
                                 session: AsyncSession = Depends(get_session)):
    user_res = await session.execute(select(User).where(User.email == pswrd_retrieve_form.email))
    user_obj = user_res.scalar()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email doesnt exists"
        )
    background_tasks.add_task(send_retrieve_password_link, user_obj, request)
    return JSONResponse({'message': 'Email to retrieve password sent'},
                        status_code=status.HTTP_200_OK)


@router.get('/auth/retrieve_password/{token}/', tags=['auth'])
async def retrieve_password(token: str,
                            session: AsyncSession = Depends(get_session)):
    """ Method to get access for retrieve password page """
    try:
        jwt_decoded = jwt.decode(
            token, settings.JWT_VERIFICATION_SECRET_KEY, settings.JWT_ALGORITHM)
        if datetime.datetime.fromtimestamp(jwt_decoded['exp']) < datetime.datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token expired"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not validate token"
        )
    user_res = await session.execute(select(User).where(User.email == jwt_decoded['email']))
    user_obj = user_res.scalar()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid code or user doesn't exist")
    return JSONResponse({"message": "Verifed to change password"},
                        status_code=status.HTTP_200_OK)


@router.post('/auth/retrieve_password/{token}/', tags=['auth'])
async def retrieve_password(token: str,
                            pswrd_form: UserPasswordRetrieve,
                            session: AsyncSession = Depends(get_session)):
    try:
        jwt_decoded = jwt.decode(
            token, settings.JWT_VERIFICATION_SECRET_KEY, settings.JWT_ALGORITHM)
        if datetime.datetime.fromtimestamp(jwt_decoded['exp']) < datetime.datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token expired"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not validate token"
        )
    user_res = await session.execute(select(User).where(User.email == jwt_decoded['email']))
    user_obj = user_res.scalar()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid code or user doesn't exist")
    user_obj.password = get_hashed_password(pswrd_form.password)
    await session.commit()
    return JSONResponse({"message": "Password changed successfully"},
                        status_code=status.HTTP_200_OK)


@router.get('/auth/verifyemail/{token}/', tags=['auth'])
async def verify(token: str,
                 session: AsyncSession = Depends(get_session)):
    try:
        jwt_decoded = jwt.decode(
            token, settings.JWT_VERIFICATION_SECRET_KEY, settings.JWT_ALGORITHM)
        if datetime.datetime.fromtimestamp(jwt_decoded['exp']) < datetime.datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token expired"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not validate token"
        )
    user_res = await session.execute(select(User).where(User.email == jwt_decoded['email']))
    user_obj = user_res.scalar()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid code or user doesn't exist")
    if user_obj.is_verifed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='Email can only be verified once')
    user_obj.is_verifed = True
    await session.commit()
    return JSONResponse({"message": "Account verified successfully"},
                        status_code=status.HTTP_200_OK)
