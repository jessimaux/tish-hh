import os
import datetime

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, Security
from fastapi.responses import JSONResponse
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import settings
from dependencies import get_session
from models import Image
from utils import handle_file_upload
from apps.auth.utils import get_hashed_password, verify_password
from apps.auth.dependencies import get_current_active_user
from apps.events.models import Event, Sign
from .models import *
from .schemas import *
from . import crud


router = APIRouter()


@router.get("/users/me/", tags=['me'], response_model=UserRetrieve)
async def get_user_me(current_user: UserRetrieve = Security(get_current_active_user, scopes=['me'])):
    return current_user


@router.post('/users/me/', tags=['me'])
async def update_user(user: UserUpdate,
                      current_user: UserRetrieve = Security(
                          get_current_active_user, scopes=['me']),
                      session: AsyncSession = Depends(get_session)):
    current_user = await crud.update_user(user, current_user, session)
    return JSONResponse({}, status_code=status.HTTP_200_OK)


# TODO: delete photo
@router.post('/users/me/photo/', tags=['me'])
async def update_photo(image: UploadFile,
                       current_user: UserRetrieve = Security(
                           get_current_active_user, scopes=['me']),
                       session: AsyncSession = Depends(get_session)):
    try:
        image_url = await handle_file_upload(image, 'auth/profile/', ['image/jpeg', 'image/png'])
        image_obj = Image(url=image_url, object_type='User',
                          object_id=current_user.id)
    finally:
        await session.execute(delete(Image).where(Image.object_id == current_user.id,
                                                  Image.object_type == 'User'))
        if current_user.image:
            file_path = os.path.join(settings.BASEDIR, current_user.image.url[1:])
            if os.path.exists(file_path):
                os.remove(file_path)
    session.add(image_obj)
    await session.commit()
    return JSONResponse({}, status_code=status.HTTP_200_OK)


@router.post('/users/me/change_password/', tags=['me'])
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
    user_obj = await crud.get_user_or_404(username=username, session=session)
    return user_obj


@router.get('/users/{username}/followers/', tags=['users'], response_model=list[UserRetrieve])
async def get_followers(username: str,
                        current_user: UserRetrieve = Security(
                            get_current_active_user, scopes=['me', 'users']),
                        session: AsyncSession = Depends(get_session)):
    user_obj = await crud.get_user_or_404(username=username, session=session)
    return (await session.scalars(user_obj.followers.statement)).all()


@router.get('/users/{username}/following/', tags=['users'], response_model=list[UserRetrieve])
async def get_following(username: str,
                        current_user: UserRetrieve = Security(
                            get_current_active_user, scopes=['me', 'users']),
                        session: AsyncSession = Depends(get_session)):
    user_obj = await crud.get_user_or_404(username=username, session=session)
    return (await session.scalars(user_obj.following.statement)).all()


@router.get('/users/{username}/is_follow/', tags=['users'])
async def is_following(username: str,
                       current_user: UserRetrieve = Security(
                           get_current_active_user, scopes=['me', 'users']),
                       session: AsyncSession = Depends(get_session)):
    user = await crud.get_user_or_404(username=username, session=session)
    if await crud.check_follow(user, current_user, session):
        return JSONResponse({}, status_code=status.HTTP_200_OK)
    else:
        return JSONResponse({}, status_code=status.HTTP_404_NOT_FOUND)


@router.post('/users/{username}/follow/', tags=['users'])
async def follow(username: str,
                 current_user: UserRetrieve = Security(
                     get_current_active_user, scopes=['me', 'users']),
                 session: AsyncSession = Depends(get_session)):
    user = await crud.get_user_or_404(username=username, session=session)
    if await crud.check_follow(user, current_user, session):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Already followed')
    else:
        subscribe_obj = Subscription(
            subscriber_id=current_user.id, publisher_id=user.id)
        session.add(subscribe_obj)
        await session.commit()
        return JSONResponse({}, status_code=status.HTTP_201_CREATED)


@router.post('/users/{username}/unfollow/', tags=['users'])
async def unfollow(username: str,
                   current_user: UserRetrieve = Security(
                       get_current_active_user, scopes=['me', 'users']),
                   session: AsyncSession = Depends(get_session)):
    user = await crud.get_user_or_404(username=username, session=session)
    subscribe_obj = (await session.execute(select(Subscription)
                                           .where(Subscription.subscriber_id == current_user.id,
                                                  Subscription.publisher_id == user.id))).scalar()
    if subscribe_obj:
        await session.delete(subscribe_obj)
        await session.commit()
        return JSONResponse({"message": "Unfollow successfully"}, status_code=status.HTTP_202_ACCEPTED)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Doesnt followed')


@router.get('/users/{username}/events/', tags=['users'])
async def get_user_events(role: str,
                          username: str,
                          current_user: UserRetrieve = Security(
                              get_current_active_user, scopes=['events', 'users']),
                          session: AsyncSession = Depends(get_session)):
    user = await crud.get_user_or_404(username=username, session=session)
    if role == 'member':
        return (await session.scalars(user.signs.statement
                                      .options(selectinload(Sign.event)))).all()
    elif role == 'creator':
        return (await session.scalars(user.signs.statement
                                      .options(selectinload(Sign.event))
                                      .where(Event.created_by == user.id))).all()
