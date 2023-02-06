from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_session
from apps.auth.dependencies import get_current_active_user
from apps.auth.schemas import UserRetrieve
from .models import *
from .schemas import *
from . import crud


router = APIRouter()


""" Catgories """

@router.get("/categories/", tags=['categories'])
async def get_categories(current_user: UserRetrieve = Depends(get_current_active_user),
                         session: AsyncSession = Depends(get_session)):
    categories_res = await session.execute(select(Category))
    categories_objs = categories_res.scalars().all()
    return categories_objs

@router.post("/categories/", tags=['categories'], response_model=CategoryBase)
async def create_category(category: CategoryBase, 
                          current_user: UserRetrieve = Depends(get_current_active_user),
                          session: AsyncSession = Depends(get_session)):
    check_name_res = await session.execute(select(Category).where(Category.name == category.name))
    check_name = check_name_res.scalar()
    if check_name:
        raise HTTPException(status_code=400, detail="Category already existed")
    category_obj = Category(name=category.name)
    session.add(category_obj)
    await session.commit()
    return category_obj

@router.get("/categories/{name}/", tags=['categories'], response_model=CategoryBase)
async def get_category(name: str, 
                       current_user: UserRetrieve = Depends(get_current_active_user),
                       session: AsyncSession = Depends(get_session)):
    category_res = await session.execute(select(Category).where(Category.name == name))
    category_obj = category_res.scalar()
    if not category_obj:
        raise HTTPException(status_code=404, detail="Category doesnt exist")
    return category_obj

# TODO: add check updated value to unique
@router.put("/categories/{name}/", tags=['categories'], response_model=CategoryBase)
async def edit_category(name: str, 
                        category: CategoryBase, 
                        current_user: UserRetrieve = Depends(get_current_active_user),
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

@router.delete("/categories/{name}/", tags=['categories'])
async def delete_category(name: str, 
                          current_user: UserRetrieve = Depends(get_current_active_user),
                          session: AsyncSession = Depends(get_session)):
    await session.execute(delete(Category).where(Category.name == name))
    await session.commit()
    return JSONResponse({"message": "Category deleted successfully"}, status_code=status.HTTP_202_ACCEPTED)


""" Tags """

@router.get("/tags/", tags=['tags'])
async def get_tags(current_user: UserRetrieve = Depends(get_current_active_user),
                   session: AsyncSession = Depends(get_session)):
    tags_res = await session.execute(select(Tag))
    tags_objs = tags_res.scalars().all()
    return tags_objs

@router.post("/tags/", tags=['tags'], response_model=TagBase)
async def create_tag(tag: TagBase, 
                     current_user: UserRetrieve = Depends(get_current_active_user),
                     session: AsyncSession = Depends(get_session)):
    check_name_res = await session.execute(select(Tag).where(Tag.name == tag.name))
    check_name = check_name_res.scalar()
    if check_name:
        raise HTTPException(status_code=400, detail="Tag already existed")
    tag_obj = Tag(name=tag.name)
    session.add(tag_obj)
    await session.commit()
    return tag_obj

@router.get("/tags/{name}/", tags=['tags'], response_model=TagBase)
async def get_tag(name: str,
                  current_user: UserRetrieve = Depends(get_current_active_user),
                  session: AsyncSession = Depends(get_session)):
    tag_obj_res = await session.execute(select(Tag).where(Tag.name == name))
    tag_obj = tag_obj_res.scalar()
    return tag_obj

@router.put("/tags/{name}/", tags=['tags'], response_model=TagBase)
async def edit_tag(name: str, 
                   tag: TagBase, 
                   current_user: UserRetrieve = Depends(get_current_active_user),
                   session: AsyncSession = Depends(get_session)):
    tag_obj_res = await session.execute(select(Tag).where(Tag.name == name))
    tag_obj = tag_obj_res.scalar()
    for attr, value in tag:
        setattr(tag_obj, attr, value)
    session.add(tag_obj)
    await session.commit()
    return tag_obj

@router.delete("/tags/{name}/", tags=['tags'])
async def delete_tag(name: str, 
                     current_user: UserRetrieve = Depends(get_current_active_user),
                     session: AsyncSession = Depends(get_session)):
    await session.execute(delete(Tag).where(Tag.name == name))
    await session.commit()
    return JSONResponse({"message": "Tag deleted successfully"}, status_code=status.HTTP_202_ACCEPTED)


""" Events """

@router.get("/events/", tags=['events'])
async def get_events(current_user: UserRetrieve = Depends(get_current_active_user),
                     session: AsyncSession = Depends(get_session)):
    events_objs_res = await session.execute(select(Event))
    events_objs = events_objs_res.scalars().all()
    return events_objs

@router.get("/events/{id}", tags=['events'], response_model=EventRetrieve)
async def get_event(id: int,
                    current_user: UserRetrieve = Depends(get_current_active_user),
                    session: AsyncSession = Depends(get_session)):
    event_obj_res = await session.execute(select(Event).where(Event.id == id))
    event_obj = event_obj_res.scalar()
    return event_obj

@router.post("/events/", tags=['events'], response_model=EventRetrieve)
async def create_event(event: EventCreate, 
                       current_user: UserRetrieve = Depends(get_current_active_user),
                       session: AsyncSession = Depends(get_session)):        
    event_obj = await crud.create_event(event, session)
    return event_obj

@router.put("/events/{id}", tags=['events'], response_model=EventRetrieve)
async def edit_event(id: int,
                     event: EventCreate,
                     current_user: UserRetrieve = Depends(get_current_active_user),
                     session: AsyncSession = Depends(get_session)):
    event_obj = await crud.edit_event(id, event, session)
    return event_obj

@router.delete('/events/{id}', tags=['events'])
async def delete_event(id: int,
                       current_user: UserRetrieve = Depends(get_current_active_user),
                       session: AsyncSession = Depends(get_session)):
    await session.execute(delete(Event).where(Event.id == id))
    await session.commit()
    return JSONResponse({"message": "Event deleted successfully"}, status_code=status.HTTP_202_ACCEPTED)


""" Sign """

@router.get("/signs/", tags=['signs'])
async def get_signs(current_user: UserRetrieve = Depends(get_current_active_user),
                    session: AsyncSession = Depends(get_session)):
    sign_res = await session.execute(select(Sign))
    sign_objs = sign_res.scalaras().all()
    return sign_objs

@router.post("/signs/", tags=['signs'], response_model=SignRetrieve)
async def create_sign(sign: SignBase, 
                      current_user: UserRetrieve = Depends(get_current_active_user),
                      session: AsyncSession = Depends(get_session)):        
    sign_obj = Sign(user_id=sign.user_id, event_id=sign.event_id, status=sign.status)
    session.add(sign_obj)
    await session.commit()
    return sign_obj

@router.put("/signs/{id}", tags=['signs'], response_model=SignRetrieve)
async def edit_sign(id: int,
                    sign: SignBase,
                    current_user: UserRetrieve = Depends(get_current_active_user),
                    session: AsyncSession = Depends(get_session)):
    sign_res = await session.execute(select(Sign).where(Sign.id == id))
    sign_obj = sign_res.scalar()
    for attr, value in sign:
        setattr(sign_obj, attr, value)
    session.add(sign_obj)
    await session.commit()
    return sign_obj

@router.delete('/signs/{id}', tags=['signs'])
async def delete_sign(id: int,
                      current_user: UserRetrieve = Depends(get_current_active_user),
                      session: AsyncSession = Depends(get_session)):
    await session.execute(delete(Sign).where(Sign.id == id))
    await session.commit()
    return JSONResponse({"message": "Sign deleted successfully"}, status_code=status.HTTP_202_ACCEPTED)
