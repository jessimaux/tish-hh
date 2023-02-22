from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.responses import JSONResponse
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_session
from apps.events.models import *
from apps.events.schemas import *
from apps.users.schemas import *
from apps.auth.dependencies import get_current_active_user


router = APIRouter()


""" Categories """

@router.post("/categories/", tags=['categories'], response_model=CategoryBase)
async def create_category(category: CategoryBase, 
                          current_user: UserRetrieve = Security(get_current_active_user, 
                                                                scopes=['categories', 'admin']),
                          session: AsyncSession = Depends(get_session)):
    check_name = (await session.execute(select(Category)
                                        .where(Category.name == category.name))).scalar()
    if check_name:
        raise HTTPException(status_code=400, detail="Category already exists")
    category_obj = Category(name=category.name)
    session.add(category_obj)
    await session.commit()
    return category_obj

@router.get("/categories/{name}/", tags=['categories'], response_model=CategoryBase)
async def get_category(name: str, 
                       current_user: UserRetrieve = Security(get_current_active_user, 
                                                             scopes=['categories', 'admin']),
                       session: AsyncSession = Depends(get_session)):
    category_res = await session.execute(select(Category).where(Category.name == name))
    category_obj = category_res.scalar()
    if not category_obj:
        raise HTTPException(status_code=404, detail="Category doesnt exist")
    return category_obj

@router.put("/categories/{name}/", tags=['categories'], response_model=CategoryBase)
async def edit_category(name: str, 
                        category: CategoryBase, 
                        current_user: UserRetrieve = Security(get_current_active_user, 
                                                              scopes=['categories', 'admin']),
                        session: AsyncSession = Depends(get_session)):
    category_obj = (await session.execute(select(Category)
                                          .where(Category.name == name))).scalar()
    check_name = (await session.execute(select(Category)
                                        .where(Category.name == category.name))).scalar()
    if check_name:
        raise HTTPException(status_code=400, detail="Category already exists")
    if not category_obj:
        raise HTTPException(status_code=404, detail="Category doesnt exist")
    for attr, value in category:
        setattr(category_obj, attr, value)
    session.add(category_obj)
    await session.commit()
    return category_obj

@router.delete("/categories/{name}/", tags=['categories'])
async def delete_category(name: str, 
                          current_user: UserRetrieve = Security(get_current_active_user, 
                                                                scopes=['categories', 'admin']),
                          session: AsyncSession = Depends(get_session)):
    await session.execute(delete(Category).where(Category.name == name))
    await session.commit()
    return JSONResponse({"message": "Category deleted successfully"}, status_code=status.HTTP_202_ACCEPTED)


""" Tags """


@router.post("/tags/", tags=['tags'], response_model=TagBase)
async def create_tag(tag: TagBase, 
                     current_user: UserRetrieve = Security(get_current_active_user, scopes=['tags', 'admin']),
                     session: AsyncSession = Depends(get_session)):
    check_name = (await session.execute(select(Tag).where(Tag.name == tag.name))).scalar()
    if check_name:
        raise HTTPException(status_code=400, detail="Tag already existed")
    tag_obj = Tag(name=tag.name)
    session.add(tag_obj)
    await session.commit()
    return tag_obj


@router.put("/tags/{name}/", tags=['tags'], response_model=TagBase)
async def edit_tag(name: str, 
                   tag: TagBase, 
                   current_user: UserRetrieve = Security(get_current_active_user, scopes=['tags', 'admin']),
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
                     current_user: UserRetrieve = Security(get_current_active_user, scopes=['tags', 'admin']),
                     session: AsyncSession = Depends(get_session)):
    await session.execute(delete(Tag).where(Tag.name == name))
    await session.commit()
    return JSONResponse({"message": "Tag deleted successfully"}, status_code=status.HTTP_202_ACCEPTED)