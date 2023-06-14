from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .models import *


class ImageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, file_name: str, user_id: int) -> Image | None:
        obj = Image(filename=file_name, created_by=user_id)
        self.session.add(obj)
        await self.session.commit()
        return obj

    async def delete(self, image_id: int, user_id: int) -> Image | None:
        result = (await self.session.execute(delete(Image)
                                             .where(Image.id == image_id, 
                                                    Image.object_type == 'User',
                                                    Image.object_id == user_id,
                                                    Image.created_by == user_id)
                                             .returning(Image))).scalar()
        await self.session.commit()
        return result

    async def link_to_user(self, image_id: int, user_id: int) -> Image | None:
        obj = (await self.session.execute(update(Image)
                                          .where(Image.id == image_id,
                                                 Image.created_by == user_id)
                                          .values(object_type='User', object_id=user_id)
                                          .returning(Image))).scalar()
        await self.session.commit()
        return obj

    async def link_to_event(self, image_id: int, user_id:int, event_id: int) -> Image | None:
        obj = (await self.session.execute(update(Image)
                                          .where(Image.id == image_id,
                                                 Image.created_by == user_id)
                                          .values(object_type='Event', object_id=event_id)
                                          .returning(Image))).scalar()
        await self.session.commit()
        return obj
