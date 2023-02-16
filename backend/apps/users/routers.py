import os
import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, \
    File, UploadFile, BackgroundTasks, Security
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

import settings
from dependencies import get_session
from email_client import send_verification_code, send_retrieve_password_link
from utils import handle_file_upload
from apps.auth.utils import get_hashed_password, verify_password
from apps.auth.dependencies import get_current_active_user
from .models import *
from .schemas import *
from . import crud


router = APIRouter()


@router.post("/users/reg/", tags=['users'], response_model=UserRetrieve)
async def create_user(user: UserCreate,
                      request: Request,
                      background_tasks: BackgroundTasks,
                      session: AsyncSession = Depends(get_session)):
    if request.headers.get("Authorization"):
        raise HTTPException(status_code=403, detail="Already authenticated")
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


@router.post('/users/send_retrieve_password/', tags=['users'])
async def send_retrieve_password(pswrd_retrieve_form: PasswordRetrieveBase,
                                 request: Request,
                                 background_tasks: BackgroundTasks,
                                 session: AsyncSession = Depends(get_session)):
    user_obj = (await session.execute(select(User).where(User.email == pswrd_retrieve_form.email))).scalar()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email doesnt exists"
        )
    background_tasks.add_task(send_retrieve_password_link, user_obj, request)
    return JSONResponse({'message': 'Email to retrieve password sent'},
                        status_code=status.HTTP_200_OK)


@router.get('/users/retrieve_password/{token}/', tags=['users'])
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
    user_obj = (await session.execute(select(User).where(User.email == jwt_decoded['email']))).scalar()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid code or user doesn't exist")
    return JSONResponse({"message": "Verifed to change password"},
                        status_code=status.HTTP_200_OK)


@router.post('/users/retrieve_password/{token}/', tags=['users'])
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
    user_obj = (await session.execute(select(User).where(User.email == jwt_decoded['email']))).scalar()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid code or user doesn't exist")
    user_obj.password = get_hashed_password(pswrd_form.password)
    await session.commit()
    return JSONResponse({"message": "Password changed successfully"},
                        status_code=status.HTTP_200_OK)


@router.get('/users/verifyemail/{token}/', tags=['users'])
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
    user_obj = (await session.execute(select(User).where(User.email == jwt_decoded['email']))).scalar()
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


@router.get("/users/me/", tags=['users-me'], response_model=UserRetrieve)
def get_user_me(current_user: UserRetrieve = Security(get_current_active_user, scopes=['me'])):
    return current_user


@router.post('/users/me/', tags=['users-me'], response_model=UserRetrieve)
async def update_user(user: UserUpdate,
                      current_user: UserRetrieve = Security(
                          get_current_active_user, scopes=['me']),
                      session: AsyncSession = Depends(get_session)):
    current_user = await crud.update_user(user, current_user, session)
    return current_user


@router.post('/users/me/photo/', tags=['users-me'])
async def update_photo(file: UploadFile,
                       current_user: UserRetrieve = Security(
                           get_current_active_user, scopes=['me']),
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
                          current_user: UserRetrieve = Security(
                              get_current_active_user, scopes=['me']),
                          session: AsyncSession = Depends(get_session)):
    if verify_password(password_form.old_password, current_user.password):
        current_user.password = get_hashed_password(password_form.new_password)
        await session.commit()
        return JSONResponse({"message": "Password changed successfully"}, status_code=status.HTTP_202_ACCEPTED)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incorrect old password"
        )


@router.get('/users/{username}/', tags=['users'], response_model=UserRetrieve)
async def get_user(username: str,
                   current_user: UserRetrieve = Security(
                       get_current_active_user, scopes=['me']),
                   session: AsyncSession = Depends(get_session)):
    user_obj = (await session.execute(select(User)
                                      .where(User.username == username))).scalar()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User with this username doesnt exist'
        )
    return user_obj


@router.get('/users/{username}/followers/', tags=['users'], response_model=list[UserRetrieve])
async def get_followers(username: str,
                        current_user: UserRetrieve = Security(
                            get_current_active_user, scopes=['me', 'users']),
                        session: AsyncSession = Depends(get_session)):
    user_obj = (await session.execute(select(User)
                                      .where(User.username == username))).scalar()
    if user_obj:
        return (await session.scalars(user_obj.followers.statement)).all()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User doesnt exist')


@router.get('/users/{username}/following/', tags=['users'], response_model=list[UserRetrieve])
async def get_following(username: str,
                        current_user: UserRetrieve = Security(
                            get_current_active_user, scopes=['me', 'users']),
                        session: AsyncSession = Depends(get_session)):
    user_obj = (await session.execute(select(User)
                                      .where(User.username == username))).scalar()
    if user_obj:
        return (await session.scalars(current_user.following.statement)).all()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User doesnt exist')


# TODO: check for user exists
@router.get('/users/{username}/is_follow/', tags=['users'])
async def is_following(username: str,
                       current_user: UserRetrieve = Security(
                           get_current_active_user, scopes=['me', 'users']),
                       session: AsyncSession = Depends(get_session)):
    target_user = (await session.execute(select(User)
                                         .where(User.username == username))).scalar()
    if await crud.check_follow(target_user, current_user, session):
        return JSONResponse(status_code=status.HTTP_200_OK)
    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND)


@router.post('/users/{username}/follow/', tags=['users'])
async def follow(username: str,
                 current_user: UserRetrieve = Security(
                     get_current_active_user, scopes=['me', 'users']),
                 session: AsyncSession = Depends(get_session)):
    target_user = (await session.execute(select(User)
                                         .where(User.username == username))).scalar()
    if target_user:
        if await crud.check_follow(target_user, current_user, session):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='Already followed')
        else:
            subscribe_obj = Subscription(
                subscriber_id=current_user.id, publisher_id=target_user.id)
            session.add(subscribe_obj)
            await session.commit()
            return JSONResponse(status_code=status.HTTP_201_CREATED)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User doesnt exist')


@router.post('/users/{username}/unfollow/', tags=['users'])
async def unfollow(username: str,
                   current_user: UserRetrieve = Security(
                       get_current_active_user, scopes=['me', 'users']),
                   session: AsyncSession = Depends(get_session)):
    user_target = (await session.execute(select(User)
                                         .where(User.username == username))).scalar()
    if user_target:
        subscribe_obj = (await session.execute(select(Subscription)
                                               .where(Subscription.subscriber_id == current_user.id,
                                                      Subscription.publisher_id == user_target.id))).scalar()
        if subscribe_obj:
            await session.delete(subscribe_obj)
            await session.commit()
            return JSONResponse({"message": "Unfollow successfully"}, status_code=status.HTTP_202_ACCEPTED)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='Doesnt followed')
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User doesnt exist')


# TODO: join event on sign
# Get events of users which he is creator
@router.get('/users/{username}/events/', tags=['users'])
async def get_user_events_creator(username: str,
                                  current_user: UserRetrieve = Security(
                                      get_current_active_user, scopes=['events', 'users']),
                                  session: AsyncSession = Depends(get_session)):
    user_target = (await session.execute(select(User)
                                         .where(User.username == username))).scalar()
    if user_target:
        return (await session.scalars(user_target.events.statement)).all()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User doesnt exist')


# Get events of users which he is membership
@router.get('/users/{username}/events/', tags=['users'])
async def get_user_events_member(username: str,
                                 current_user: UserRetrieve = Security(
                                     get_current_active_user, scopes=['events', 'users']),
                                 session: AsyncSession = Depends(get_session)):
    pass