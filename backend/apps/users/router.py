from fastapi import APIRouter, Depends, HTTPException, status, Security, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_session
from apps.auth.dependencies import get_current_active_user
from apps.events.models import Event, Sign
from .models import *
from .schemas import *
from .services import *


user_router = APIRouter()


@user_router.get("/users/me/", tags=['profile'], response_model=UserRetrieve)
async def get_current_user(current_user: UserRetrieve = Security(get_current_active_user, scopes=['profile'])):
    return current_user


@user_router.post("/users/registration/", tags=["users"], status_code=status.HTTP_201_CREATED, response_model=UserRetrieve)
async def create_user(user: UserCreate,
                      request: Request,
                      background_tasks: BackgroundTasks,
                      session: AsyncSession = Depends(get_session)):
    return await UserService(session).create_user(user, request, background_tasks)


@user_router.put('/users/me/', tags=['profile'], response_model=UserRetrieve)
async def update_user(user: UserUpdate,
                      current_user: UserRetrieve = Security(get_current_active_user, scopes=['profile']),
                      session: AsyncSession = Depends(get_session)):
    return await UserService(session).update_user(current_user.id, user)


@user_router.put('/users/me/link', tags=['profile'], response_model=list[LinkBase])
async def update_user_link(links: list[LinkBase],
                           current_user: UserRetrieve = Security(get_current_active_user, scopes=['profile']),
                           session: AsyncSession = Depends(get_session)):
    return await UserService(session).update_links(current_user.id, links)


@user_router.put('/users/me/photo/', tags=['profile'], response_model=ImageBase)
async def upload_photo(image_id: int,
                       current_user: UserRetrieve = Security(get_current_active_user, scopes=['profile']),
                       session: AsyncSession = Depends(get_session)):
    return await UserService(session).upload_photo(image_id, current_user.id)


@user_router.delete('/users/me/photo/', tags=['profile'])
async def delete_photo(image_id: int,
                       current_user: UserRetrieve = Security(get_current_active_user, scopes=['profile']),
                       session: AsyncSession = Depends(get_session)):
    deleted_rows = await UserService(session).delete_photo(image_id, current_user.id)
    if deleted_rows != 0:
        return JSONResponse({}, status_code=status.HTTP_200_OK)
    else:
        return JSONResponse({'message': 'No objects to delete'}, status_code=status.HTTP_400_BAD_REQUEST)


@user_router.post('/users/me/change_password/', tags=['profile'])
async def change_password(password_form: UserPasswordChange,
                          current_user: UserRetrieve = Security(get_current_active_user, scopes=['profile']),
                          session: AsyncSession = Depends(get_session)):
    password_updated = await UserService(session).change_password(password_form, current_user.id)
    if password_updated != 0:
        return JSONResponse({"message": "Password changed successfully"}, status_code=status.HTTP_202_ACCEPTED)
    else:
        return JSONResponse({"message": "Something going wrong"}, status_code=status.HTTP_400_BAD_REQUEST)


@user_router.post("/users/send_retrieve_password/", tags=["users"])
async def send_retrieve_password(password_retrieve_form: PasswordRetrieveBase,
                                 request: Request,
                                 background_tasks: BackgroundTasks,
                                 session: AsyncSession = Depends(get_session)):
    await UserService(session).send_retrieve_password(password_retrieve_form, request, background_tasks)


@user_router.get("/users/retrieve_password/{token}/", tags=["users"])
async def check_retrieve_password(token: str,
                                  session: AsyncSession = Depends(get_session)):
    if await UserService(session).check_retrieve_password_token(token):
        return JSONResponse({"message": "Verifed to change password"},
                            status_code=status.HTTP_200_OK)
    else:
        return JSONResponse({}, status_code=status.HTTP_403_FORBIDDEN)


@user_router.post("/users/retrieve_password/{token}/", tags=["users"])
async def retrieve_password(token: str,
                            session: AsyncSession = Depends(get_session)):
    if await UserService(session).retrieve_password(token) != 0:
        return JSONResponse({"message": "Password changed successfully"},
                            status_code=status.HTTP_200_OK)
    else:
        return JSONResponse({}, status_code=status.HTTP_400_BAD_REQUEST)


@user_router.get("/auth/verifyemail/{token}/", tags=["users"])
async def verify_email(token: str,
                       session: AsyncSession = Depends(get_session)):
    if await UserService(session).verify_email(token) != 0:
        return JSONResponse({"message": "Account verified successfully"},
                            status_code=status.HTTP_200_OK)
    else:
        return JSONResponse({}, status_code=status.HTTP_400_BAD_REQUEST)


@user_router.get('/users/me/notifications/', tags=['profile'])
async def get_notifications(current_user: UserRetrieve = Security(get_current_active_user, scopes=['profile']),
                            session: AsyncSession = Depends(get_session)):
    return (await session.scalars(current_user.notifications)).all()


@user_router.get('/users/{username}/', tags=['users'])
async def get_profile(username: str,
                      current_user: UserRetrieve = Security(get_current_active_user, scopes=['users']),
                      session: AsyncSession = Depends(get_session)):
    return await ProfileService(session).get_profile(username)


@user_router.get('/users/{username}/followers/', tags=['users'], response_model=list[UserRetrieve])
async def get_followers(username: str,
                        current_user: UserRetrieve = Security(get_current_active_user, scopes=['users']),
                        session: AsyncSession = Depends(get_session)):
    return await ProfileService(session).get_followers(username)


@user_router.get('/users/{username}/following/', tags=['users'], response_model=list[UserRetrieve])
async def get_following(username: str,
                        current_user: UserRetrieve = Security(get_current_active_user, scopes=['users']),
                        session: AsyncSession = Depends(get_session)):
    return await ProfileService(session).get_following(username)


@user_router.get('/users/{username}/is_follow/', tags=['users'])
async def is_following(username: str,
                       current_user: UserRetrieve = Security(get_current_active_user, scopes=['users']),
                       session: AsyncSession = Depends(get_session)):
    follow_status = await SubscriptionService(session).check_follow(username, current_user.id)
    return JSONResponse({'follow_status': follow_status},
                        status_code=status.HTTP_200_OK)


@user_router.post('/users/{username}/follow/', tags=['users'])
async def follow(username: str,
                 current_user: UserRetrieve = Security(get_current_active_user, scopes=['profile', 'users']),
                 session: AsyncSession = Depends(get_session)):
    result = await SubscriptionService(session).follow(username, current_user.id)
    if result:
        return JSONResponse({}, status_code=status.HTTP_201_CREATED)
    else:
        return JSONResponse({}, status_code=status.HTTP_400_BAD_REQUEST)


@user_router.post('/users/{username}/unfollow/', tags=['users'])
async def unfollow(username: str,
                   current_user: UserRetrieve = Security(get_current_active_user, scopes=['profile', 'users']),
                   session: AsyncSession = Depends(get_session)):
    result = await SubscriptionService(session).follow(username, current_user.id)
    if result:
        return JSONResponse({}, status_code=status.HTTP_200_OK)
    else:
        return JSONResponse({}, status_code=status.HTTP_400_BAD_REQUEST)


# @user_router.get('/users/{username}/events/', tags=['users'])
# async def get_user_events(role: str,
#                           username: str,
#                           current_user: UserRetrieve = Security(get_current_active_user, scopes=['users']),
#                           session: AsyncSession = Depends(get_session)):
#     user = await crud.get_user_or_404(username=username, session=session)
#     return (await session.scalars(user.signs.statement
#                                   .where(Sign.role == role)
#                                   .options(selectinload(Sign.event)))).all()
