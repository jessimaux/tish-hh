import os

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, Security
from fastapi.responses import JSONResponse
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import settings
from dependencies import get_session
from apps.core.models import Image
from apps.core.utils import handle_file_upload
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


@router.put('/users/me/', tags=['me'])
async def update_user(user: UserUpdate,
                      current_user: UserRetrieve = Security(
                          get_current_active_user, scopes=['me']),
                      session: AsyncSession = Depends(get_session)):
    current_user = await crud.update_user(user, current_user, session)
    return JSONResponse({}, status_code=status.HTTP_200_OK)


@router.put('/users/me/photo/', tags=['me'])
async def update_photo(image_id: int,
                       current_user: UserRetrieve = Security(
                           get_current_active_user, scopes=['me']),
                       session: AsyncSession = Depends(get_session)):
    try:
        image_obj = (await session.execute(select(Image)
                                            .where(Image.id == image_id))).scalar()
        image_obj.object_type = 'User'
        image_obj.object_id = current_user.id
    finally:
        file_path = os.path.join(settings.BASEDIR, current_user.image.url[1:])
        if os.path.exists(file_path):
                os.remove(file_path)
        await session.execute(delete(Image).where(Image.id == current_user.image.id))
    await session.commit()
    return JSONResponse({}, status_code=status.HTTP_200_OK)


@router.delete('/users/me/photo/', tags=['me'])
async def delete_photo(current_user: UserRetrieve = Security(
                           get_current_active_user, scopes=['me']),
                       session: AsyncSession = Depends(get_session)):
    file_path = os.path.join(settings.BASEDIR, current_user.image.url[1:])
    if os.path.exists(file_path):
            os.remove(file_path)
    await session.execute(delete(Image).where(Image.id == current_user.image.id))
    await session.commit()
    return JSONResponse({}, status_code=status.HTTP_202_ACCEPTED)


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


@router.get('/users/me/notifications/', tags=['me'])
async def get_notifications(current_user: UserRetrieve = Security(get_current_active_user, scopes=['me']),
                            session: AsyncSession = Depends(get_session)):
    return (await session.scalars(current_user.notifications)).all()


@router.get('/users/{username}/', tags=['users'])
async def get_user(username: str,
                   current_user: UserRetrieve = Security(
                       get_current_active_user, scopes=['me']),
                   session: AsyncSession = Depends(get_session)):
    subq_events = (select(func.count('*')).select_from(Event)
                      .where(Event.created_by == current_user.id)
                      .subquery())
    subq_followers = (select(func.count('*')).select_from(Subscription)
                      .where(Subscription.publisher_id == current_user.id)
                      .subquery())
    subq_following = (select(func.count('*')).select_from(Subscription)
                      .where(Subscription.subscriber_id == current_user.id)
                      .subquery())
    user = (await session.execute(select(User, subq_events, subq_followers, subq_following)
                                  .where(User.username == username))).first()
    return UserGet(**user[0].__dict__, 
                   events_count=user[1],
                   followers_count=user[2], 
                   following_count=user[3])


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
