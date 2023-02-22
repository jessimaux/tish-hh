from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.responses import JSONResponse
from sqlalchemy import select, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from dependencies import get_session
from apps.auth.dependencies import get_current_active_user
from apps.users.schemas import UserRetrieve
from .models import *
from .schemas import *
from . import crud


router = APIRouter()


""" Catgories """


@router.get("/categories/", tags=['categories'])
async def get_categories(current_user: UserRetrieve = Security(get_current_active_user, scopes=['categories']),
                         session: AsyncSession = Depends(get_session)):
    categories_res = await session.execute(select(Category))
    categories_objs = categories_res.scalars().all()
    return categories_objs


# TODO: add filter by tags
@router.get("/categories/{category_name}/", tags=['categories'], response_model=list[EventBase])
async def get_events_from_category(category_name: str,
                                   tag: str | None = None,
                                   current_user: UserRetrieve = Security(
                                       get_current_active_user, scopes=['categories']),
                                   session: AsyncSession = Depends(get_session)):
    category = await crud.get_category_or_404(session, category_name)
    statement = (select(Event)
                 .join(TagEvent, TagEvent.event_id == Event.id)
                 .join(Tag, Tag.id == TagEvent.tag_id)
                 .where(Event.category_id == category.id))
    if tag:
        statement = statement.where(Tag.name.ilike(tag))
    events = (await session.execute(statement)).scalars().all()
    return events


""" Tags """


@router.get("/tags/", tags=['tags'])
async def get_tags(current_user: UserRetrieve = Security(get_current_active_user, scopes=['tags']),
                   session: AsyncSession = Depends(get_session)):
    tags_res = await session.execute(select(Tag))
    tags_objs = tags_res.scalars().all()
    return tags_objs


""" Events """


@router.get("/events/", tags=['events'])
async def get_events(tags: str | None = None,
                     current_user: UserRetrieve = Security(get_current_active_user, scopes=['events']),
                     session: AsyncSession = Depends(get_session)):
    statement = (select(Event)
                 .join(Event.tags, isouter=True))
    # statement = (select(Event)
    #              .join(TagEvent, TagEvent.event_id == Event.id, isouter=True)
    #              .join(Tag, Tag.id == TagEvent.tag_id, isouter=True ))
    if tags:
        filters = None
        tags_list = tags.split(' ')
        for tag in tags_list:
            if filters is not None:
                filters |= Tag.name.ilike(tag)
            else:
                filters = Tag.name.ilike(tag)
        statement = statement.where(filters)
    events = (await session.execute(statement.distinct(Event.id)))
    return events.scalars().all()


@router.get("/events/{id}/", tags=['events'], response_model=EventRetrieve)
async def get_event(id: int,
                    current_user: UserRetrieve = Security(
                        get_current_active_user, scopes=['events']),
                    session: AsyncSession = Depends(get_session)):
    event_obj = await crud.get_event(id, session)
    return event_obj


@router.post("/events/", tags=['events'], response_model=EventRetrieve)
async def create_event(event: EventCreate,
                       current_user: UserRetrieve = Security(
                           get_current_active_user, scopes=['events']),
                       session: AsyncSession = Depends(get_session)):
    event_obj = await crud.create_event(event, session)
    return event_obj


@router.put("/events/{id}/", tags=['events'], response_model=EventRetrieve)
async def edit_event(id: int,
                     event: EventCreate,
                     current_user: UserRetrieve = Security(
                         get_current_active_user, scopes=['events']),
                     session: AsyncSession = Depends(get_session)):
    event_obj = await crud.get_event(id, session)
    # TODO: check created_by empty?
    # if event_obj.created_by != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
    #                         detail="Not enough permissions")
    event_obj = await crud.edit_event(event, event_obj, session)
    return event_obj


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


@router.post("/signs/", tags=['signs'], response_model=SignRetrieve)
async def create_sign(sign: SignBase,
                      current_user: UserRetrieve = Security(
                          get_current_active_user, scopes=['signs']),
                      session: AsyncSession = Depends(get_session)):
    sign_obj = Sign(user_id=current_user.id,
                    event_id=sign.event_id, status=sign.status)
    session.add(sign_obj)
    await session.commit()
    return sign_obj


@router.put("/signs/{id}", tags=['signs'], response_model=SignRetrieve)
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
    return sign_obj


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
    return JSONResponse({"message": "Sign deleted successfully"}, status_code=status.HTTP_202_ACCEPTED)
