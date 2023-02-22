from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import Base


async def update_fg(fg_objects: list, model: Base, data: list, session: AsyncSession) -> None:
    """ 
    Method to allow update foreign key objects.
    
    Args:
        fg_objs: List of foreign key objects.
        model: Model of foreign key object.
        data: Income data from request.
        session: Session for db access.
    """
    # take element from request
    for element in data:
        # if it have id - update it, else - create
        if element.id:
            for fg_obj in fg_objects:
                if fg_obj.id == element.id:
                    for attr, value in element:
                        setattr(fg_obj, attr, value)
        else:
            fg_objects.append(model(**element.dict()))
    
    # delete obj if it doesnt in request
    for fg_obj in fg_objects:
        if fg_obj.id not in [element.id for element in data]:
            fg_objects.remove(fg_obj)
            await session.delete(fg_obj)
