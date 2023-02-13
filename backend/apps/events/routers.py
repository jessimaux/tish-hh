from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.responses import JSONResponse
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from dependencies import get_session
from apps.auth.dependencies import get_current_active_user
from apps.auth.schemas import UserRetrieve
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

# TODO: Only for admin
@router.post("/categories/", tags=['categories'], response_model=CategoryBase)
async def create_category(category: CategoryBase, 
                          current_user: UserRetrieve = Security(get_current_active_user, scopes=['categories']),
                          session: AsyncSession = Depends(get_session)):
    check_name_res = await session.execute(select(Category).where(Category.name == category.name))
    check_name = check_name_res.scalar()
    if check_name:
        raise HTTPException(status_code=400, detail="Category already existed")
    category_obj = Category(name=category.name)
    session.add(category_obj)
    await session.commit()
    return category_obj

# TODO: Doesnt need
@router.get("/categories/{name}/", tags=['categories'], response_model=CategoryBase)
async def get_category(name: str, 
                       current_user: UserRetrieve = Security(get_current_active_user, scopes=['categories']),
                       session: AsyncSession = Depends(get_session)):
    category_res = await session.execute(select(Category).where(Category.name == name))
    category_obj = category_res.scalar()
    if not category_obj:
        raise HTTPException(status_code=404, detail="Category doesnt exist")
    return category_obj

# TODO: Only for admin
# TODO: add check updated value to unique
@router.put("/categories/{name}/", tags=['categories'], response_model=CategoryBase)
async def edit_category(name: str, 
                        category: CategoryBase, 
                        current_user: UserRetrieve = Security(get_current_active_user, scopes=['categories']),
                        session: AsyncSession = Depends(get_session)):
    category_res = await session.execute(select(Category).where(Category.name == name))
    category_obj = category_res.scalar()
    if not category_obj:
        raise HTTPException(status_code=404, detail="Category doesnt exist")
    for attr, value in category:
        setattr(category_obj, attr, value)
    session.add(category_obj)
    await session.commit()
    return category_obj

# TODO: Only for admin
@router.delete("/categories/{name}/", tags=['categories'])
async def delete_category(name: str, 
                          current_user: UserRetrieve = Security(get_current_active_user, scopes=['categories']),
                          session: AsyncSession = Depends(get_session)):
    await session.execute(delete(Category).where(Category.name == name))
    await session.commit()
    return JSONResponse({"message": "Category deleted successfully"}, status_code=status.HTTP_202_ACCEPTED)


""" Tags """

@router.get("/tags/", tags=['tags'])
async def get_tags(current_user: UserRetrieve = Security(get_current_active_user, scopes=['tags']),
                   session: AsyncSession = Depends(get_session)):
    tags_res = await session.execute(select(Tag))
    tags_objs = tags_res.scalars().all()
    return tags_objs

# TODO: only for admin
@router.post("/tags/", tags=['tags'], response_model=TagBase)
async def create_tag(tag: TagBase, 
                     current_user: UserRetrieve = Security(get_current_active_user, scopes=['tags']),
                     session: AsyncSession = Depends(get_session)):
    check_name_res = await session.execute(select(Tag).where(Tag.name == tag.name))
    check_name = check_name_res.scalar()
    if check_name:
        raise HTTPException(status_code=400, detail="Tag already existed")
    tag_obj = Tag(name=tag.name)
    session.add(tag_obj)
    await session.commit()
    return tag_obj

# TODO: Doesnt need
@router.get("/tags/{name}/", tags=['tags'], response_model=TagBase)
async def get_tag(name: str,
                  current_user: UserRetrieve = Security(get_current_active_user, scopes=['tags']),
                  session: AsyncSession = Depends(get_session)):
    tag_obj_res = await session.execute(select(Tag).where(Tag.name == name))
    tag_obj = tag_obj_res.scalar()
    return tag_obj

# TODO: Only for admin
@router.put("/tags/{name}/", tags=['tags'], response_model=TagBase)
async def edit_tag(name: str, 
                   tag: TagBase, 
                   current_user: UserRetrieve = Security(get_current_active_user, scopes=['tags']),
                   session: AsyncSession = Depends(get_session)):
    tag_obj_res = await session.execute(select(Tag).where(Tag.name == name))
    tag_obj = tag_obj_res.scalar()
    for attr, value in tag:
        setattr(tag_obj, attr, value)
    session.add(tag_obj)
    await session.commit()
    return tag_obj

# TODO: Only for admin
@router.delete("/tags/{name}/", tags=['tags'])
async def delete_tag(name: str, 
                     current_user: UserRetrieve = Security(get_current_active_user, scopes=['tags']),
                     session: AsyncSession = Depends(get_session)):
    await session.execute(delete(Tag).where(Tag.name == name))
    await session.commit()
    return JSONResponse({"message": "Tag deleted successfully"}, status_code=status.HTTP_202_ACCEPTED)


""" Events """

@router.get("/events/", tags=['events'])
async def get_events(current_user: UserRetrieve = Security(get_current_active_user, scopes=['events']),
                     session: AsyncSession = Depends(get_session)):
    events_objs_res = await session.execute(select(Event))
    events_objs = events_objs_res.scalars().all()
    return events_objs

@router.get("/events/{id}", tags=['events'], response_model=EventRetrieve)
async def get_event(id: int,
                    current_user: UserRetrieve = Security(get_current_active_user, scopes=['events']),
                    session: AsyncSession = Depends(get_session)):
    event_obj = await crud.get_event(id, session)
    return event_obj

@router.post("/events/", tags=['events'], response_model=EventRetrieve)
async def create_event(event: EventCreate, 
                       current_user: UserRetrieve = Security(get_current_active_user, scopes=['events']),
                       session: AsyncSession = Depends(get_session)):        
    event_obj = await crud.create_event(event, session)
    return event_obj

@router.put("/events/{id}", tags=['events'], response_model=EventRetrieve)
async def edit_event(id: int,
                     event: EventCreate,
                     current_user: UserRetrieve = Security(get_current_active_user, scopes=['events']),
                     session: AsyncSession = Depends(get_session)):
    event_obj = await get_event(id, session)
    if event_obj.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not enough permissions")
    event_obj = await crud.edit_event(event, event_obj, session)
    return event_obj

@router.delete('/events/{id}', tags=['events'])
async def delete_event(id: int,
                       current_user: UserRetrieve = Security(get_current_active_user, scopes=['events']),
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
                      current_user: UserRetrieve = Security(get_current_active_user, scopes=['signs']),
                      session: AsyncSession = Depends(get_session)):        
    sign_obj = Sign(user_id=current_user.id, event_id=sign.event_id, status=sign.status)
    session.add(sign_obj)
    await session.commit()
    return sign_obj

@router.put("/signs/{id}", tags=['signs'], response_model=SignRetrieve)
async def edit_sign(id: int,
                    sign: SignBase,
                    current_user: UserRetrieve = Security(get_current_active_user, scopes=['signs']),
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
                      current_user: UserRetrieve = Security(get_current_active_user, scopes=['signs']),
                      session: AsyncSession = Depends(get_session)):
    sign_obj = (await session.execute(select(Sign).where(Sign.id == id))).scalar()
    if not sign_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Sign doesnt exist')
    await session.delete(sign_obj)
    await session.commit()
    return JSONResponse({"message": "Sign deleted successfully"}, status_code=status.HTTP_202_ACCEPTED)
