from apps.auth.dependencies import get_current_active_user
from apps.users.schemas import UserRetrieve
from database import get_session
from fastapi import (APIRouter, Depends, HTTPException, Query, Security,
                     UploadFile, status)
from fastapi.responses import JSONResponse
from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from . import crud
from .models import *
from .schemas import *
from .services import *

router = APIRouter()


""" Catgories """


@router.get("/categories/", tags=['categories'], response_model=list[CategoryRetrieve])
async def get_categories(current_user: UserRetrieve = Security(get_current_active_user, scopes=['events']),
                         session: AsyncSession = Depends(get_session)):
    return await CategoryService(session).get_categories()


""" Tags """


@router.get("/tags/", tags=['tags'], response_model=list[TagBase])
async def get_tags(current_user: UserRetrieve = Security(get_current_active_user, scopes=['tags']),
                   session: AsyncSession = Depends(get_session)):
    return await TagService(session).get_all()


""" Events """


@router.get("/events/", tags=['events'], response_model=list[EventBase])
async def get_events(current_user: UserRetrieve = Security(
        get_current_active_user, scopes=['events']),
        session: AsyncSession = Depends(get_session)):
    return await EventService(session).get_all()


# TODO: add filter by tag
@router.get("/categories/{category_name}/", tags=['categories'], response_model=list[EventBase])
async def get_events_from_category(category_name: str,
                                   current_user: UserRetrieve = Security(
                                       get_current_active_user, scopes=['categories']),
                                   session: AsyncSession = Depends(get_session)):
    return await EventService(session).get_from_category(category_name)


@router.get("/events/{event_id}/", tags=['events'], response_model=EventRetrieve)
async def get_event(event_id: int,
                    current_user: UserRetrieve = Security(
                        get_current_active_user, scopes=['events']),
                    session: AsyncSession = Depends(get_session)):
    return await EventService(session).get(event_id)


@router.post("/events/", tags=['events'])
async def create_event(event: EventCreate,
                       current_user: UserRetrieve = Security(
                           get_current_active_user, scopes=['events']),
                       session: AsyncSession = Depends(get_session)):
    return await EventService(session).create(event, current_user.id)


@router.put("/events/{id}/", tags=['events'])
async def edit_event(id: int,
                     event: EventCreate,
                     current_user: UserRetrieve = Security(
                         get_current_active_user, scopes=['events']),
                     session: AsyncSession = Depends(get_session)):
    event_obj = await crud.get_event(id, session)
    # check on current user is owner
    if event_obj.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not enough permissions")
    event_obj = await crud.edit_event(event, event_obj, session)
    return JSONResponse({}, status_code=status.HTTP_200_OK)


@router.delete('/events/{id}/', tags=['events'])
async def delete_event(id: int,
                       current_user: UserRetrieve = Security(
                           get_current_active_user, scopes=['events']),
                       session: AsyncSession = Depends(get_session)):
    event_obj = (await session.execute(select(Event).where(Event.id == id))).scalar()
    if not event_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Event doesnt exist')
    await session.delete(event_obj)
    await session.commit()
    return JSONResponse({"message": "Event deleted successfully"}, status_code=status.HTTP_202_ACCEPTED)


""" Sign """


@router.get("/signs/", tags=['signs'])
async def get_signs(current_user: UserRetrieve = Security(get_current_active_user, scopes=['signs']),
                    session: AsyncSession = Depends(get_session)):
    sign_res = await session.execute(select(Sign))
    sign_objs = sign_res.scalars().all()
    return sign_objs


@router.post("/signs/", tags=['signs'])
async def create_sign(sign: SignBase,
                      current_user: UserRetrieve = Security(
                          get_current_active_user, scopes=['signs']),
                      session: AsyncSession = Depends(get_session)):
    sign_obj = Sign(user_id=current_user.id,
                    event_id=sign.event_id, status=sign.status)
    session.add(sign_obj)
    await session.commit()
    return JSONResponse({}, status_code=status.HTTP_201_CREATED)


@router.put("/signs/{id}", tags=['signs'])
async def edit_sign(id: int,
                    sign: SignBase,
                    current_user: UserRetrieve = Security(
                        get_current_active_user, scopes=['signs']),
                    session: AsyncSession = Depends(get_session)):
    sign_obj = (await session.execute(select(Sign).where(Sign.id == id))).scalar()
    if sign_obj.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not enough permissions")
    for attr, value in sign:
        setattr(sign_obj, attr, value)
    session.add(sign_obj)
    await session.commit()
    return JSONResponse({}, status_code=status.HTTP_200_OK)


@router.delete('/signs/{id}', tags=['signs'])
async def delete_sign(id: int,
                      current_user: UserRetrieve = Security(
                          get_current_active_user, scopes=['signs']),
                      session: AsyncSession = Depends(get_session)):
    sign_obj = (await session.execute(select(Sign).where(Sign.id == id))).scalar()
    if not sign_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Sign doesnt exist')
    await session.delete(sign_obj)
    await session.commit()
    return JSONResponse({"message": "Sign deletedu successfully"}, status_code=status.HTTP_202_ACCEPTED)


@router.get('/events/{event_id}/commentaries/', tags=['commentaries'], response_model=list[CommentaryBase])
async def get_commentaries(event_id: int,
                           current_user: UserRetrieve = Security(
                               get_current_active_user, scopes=['signs']),
                           session: AsyncSession = Depends(get_session)):
    commentaries = (await session.execute(select(Commentary)
                                          .where(Commentary.event_id == event_id))).scalars().all()
    return commentaries


@router.post('/events/{event_id}/commentaries/', tags=['commentaries'])
async def create_commentary(event_id: int,
                            commentary: CommentaryBase,
                            current_user: UserRetrieve = Security(
                                get_current_active_user, scopes=['signs']),
                            session: AsyncSession = Depends(get_session)):
    commentary_obj = Commentary(event_id=event_id, content=commentary.content)
    session.add(commentary_obj)
    await session.commit()
    return JSONResponse({}, status_code=status.HTTP_201_CREATED)


@router.put('/events/{event_id}/commentaries/{commentary_id}', tags=['commentaries'])
async def edit_commentary(event_id: int,
                          commentary_id: int,
                          commentary: CommentaryBase,
                          current_user: UserRetrieve = Security(
                              get_current_active_user, scopes=['signs']),
                          session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(update(Commentary)
                              .where(Commentary.id == commentary_id,
                                     Commentary.event_id == event_id,
                                     Commentary.created_by == current_user.id)
                              .values(content=commentary.content))
    except:
        return JSONResponse({}, status_code=status.HTTP_403_FORBIDDEN)
    finally:
        return JSONResponse({}, status_code=status.HTTP_200_OK)


@router.delete('/commentaries/{commentary_id}', tags=['commentaries'])
async def delete_commentary(commentary_id: int,
                            current_user: UserRetrieve = Security(
                                get_current_active_user, scopes=['signs']),
                            session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(delete(Commentary)
                              .where(Commentary.id == commentary_id,
                                     Commentary.created_by == current_user.id))
    except:
        return JSONResponse({}, status_code=status.HTTP_403_FORBIDDEN)
    finally:
        return JSONResponse({"message": "Sign deletedu successfully"}, status_code=status.HTTP_202_ACCEPTED)


@router.get('/likes/', tags=['likes'], response_model=list[LikeBase])
async def get_likes(current_user: UserRetrieve = Security(
        get_current_active_user, scopes=['signs']),
        session: AsyncSession = Depends(get_session)):
    likes_obj = (await session.execute(select(Like)
                                       .where(Like.user_id == current_user.id)
                                       .options(selectinload(Like.event)))).scalars().all()
    return likes_obj


@router.post('/events/{event_id}/like/', tags=['likes'])
async def create_likes(event_id: int,
                       current_user: UserRetrieve = Security(
                           get_current_active_user, scopes=['signs']),
                       session: AsyncSession = Depends(get_session)):
    like_obj = Like(event_id=event_id, user_id=current_user.id)
    session.add(like_obj)
    await session.commit()
    return JSONResponse({}, status_code=status.HTTP_201_CREATED)


@router.post('/likes/{id}/', tags=['likes'])
async def delete_like(id: int,
                      current_user: UserRetrieve = Security(
                          get_current_active_user, scopes=['signs']),
                      session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(delete(Like)
                              .where(Like.id == id,
                                     Like.user_id == current_user.id))
    except:
        return JSONResponse({}, status_code=status.HTTP_403_FORBIDDEN)
    finally:
        return JSONResponse({"message": "Sign deletedu successfully"}, status_code=status.HTTP_202_ACCEPTED)
