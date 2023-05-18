from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import settings

SQLALCHEMY_DATABASE_URL = f"{settings.DB_ENGINE}://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def update_foreign_key(foreign_key_objs: list, model: Base, data: list, session: AsyncSession) -> None:
    """ Method to allow update foreign key objects. """
    # if object has id - update it, else - create
    for element in data:
        if element.id:
            for fg_obj in foreign_key_objs:
                if fg_obj.id == element.id:
                    for attr, value in element:
                        setattr(fg_obj, attr, value)
        else:
            foreign_key_objs.append(model(**element.dict()))

    # delete obj if it doesnt in request
    for fg_obj in foreign_key_objs:
        if fg_obj.id not in [element.id for element in data]:
            foreign_key_objs.remove(fg_obj)
            await session.delete(fg_obj)
