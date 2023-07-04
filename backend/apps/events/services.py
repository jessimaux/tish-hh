from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.uploader.repository import ImageRepository
from .repository import *
from .schemas import *


class CategoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.category_repository = CategoryRepository(session)

    async def get_categories(self) -> list[CategoryRetrieve]:
        category_objs = await self.category_repository.get_all_with_meta()
        return [CategoryRetrieve(category) for category in category_objs]


class EventService:
    def __init__(self, session: AsyncSession) -> None:
        self.tag_service = TagService(session)
        self.event_repository = EventRepository(session)
        self.sign_repository = SignRepository(session)
        self.characteristic_repository = CharacteristicRepository(session)
        self.qa_repository = QARepository(session)
        self.image_repository = ImageRepository(session)

    async def get_all(self) -> list[EventBase]:
        event_objs = self.event_repository.get_all()
        return [EventBase(event) for event in event_objs]

    async def get_from_category(self, category_name: str) -> list[EventBase]:
        event_objs = await self.event_repository.get_from_category(category_name)
        return [EventBase(event) for event in event_objs]

    async def get(self, event_id: int) -> EventRetrieve:
        event_obj = self.event_repository.get(event_id)
        return EventRetrieve(event_obj)

    # TODO: transaction rollback if something going wrong
    async def create(self, event: EventCreate, current_user_id: int) -> EventRetrieve | None:
        event_general = dict()
        for attr, value in event:
            if attr in ['tags', 'characteristics', 'qas', 'images']:
                event_general[attr] = value
        event_general['created_by'] = current_user_id
        event_obj = await self.event_repository.create(event_general)
        await self.tag_service.create_event_tags(event_obj.id, event.tags)
        
        for characteristic_description in event.characteristics_description:
            await self.characteristic_repository.link_to_event(characteristic_description.description,
                                                               characteristic_description.characteristic.id,
                                                               event_obj.id)

        for qa in event.qas:
            await self.qa_repository.create(qa.dict())

        for image_id in event.images:
            await self.image_repository.link_to_event(image_id, current_user_id, event_obj.id)

        await self.sign_repository.create(current_user_id, event_obj.id, 'creator')

        return EventRetrieve(event_obj)
    
    async def update(self, event: EventCreate, user_id: int) -> EventRetrieve | None:
        event_general = dict()
        for attr, value in event:
            if attr in ['tags', 'characteristics', 'qas', 'images']:
                event_general[attr] = value
        event_obj = await self.event_repository.update(event_general, user_id)
        await self.tag_service.update_event_tags(event.id, event.tags)

        for characteristic_description in event.characteristics_description:
            await self.characteristic_repository.link_to_event(characteristic_description.description,
                                                               characteristic_description.characteristic.id,
                                                               event_obj.id)

        for qa in event.qas:
            await self.qa_repository.create(qa.dict())

        for image_id in event.images:
            await self.image_repository.link_to_event(image_id, user_id, event_obj.id)

        await self.sign_repository.create(user_id, event_obj.id, 'creator')

        return EventRetrieve(event_obj)
    
    async def delete(self, event_id: int, user_id: int) -> bool:
        if await self.event_repository.delete(event_id, user_id):
            return True
        else:
            return False


class TagService:
    def __init__(self, session: AsyncSession) -> None:
        self.tag_repository = TagRepository(session)

    async def get_all(self) -> list[TagBase]:
        tag_objs = await self.tag_repository.get_all()
        return [TagBase(tag) for tag in tag_objs]
    
    async def create_event_tags(self, event_id: int, tags: list[TagBase]):
        for tag in tags:
            tag_obj = await self.tag_repository.get(tag.name)
            if not tag_obj:
                tag_obj = await self.tag_repository.create(tag.name)
            await self.tag_repository.link_to_event(tag_obj.id, event_id)

    async def update_event_tags(self, event_id: int, tags: list[TagBase]):
        tag_ids_from_db = [tag.id for tag in await self.tag_repository.get_by_event(event_id)]
        for tag in tags:
            if tag.id not in tag_ids_from_db:
                await self.tag_repository.link_to_event(tag.id, event_id)
        
        tag_ids_from_request = [tag.id for tag in tags]
        for tag_id in tag_ids_from_db:
            if tag_id not in tag_ids_from_request:
                await self.tag_repository.unlink_to_event(tag_id, event_id)
                
                
class SignService:
    def __init__(self, session: AsyncSession) -> None:
        self.sign_repository = SignRepository(session)
        
    async def get_by_event(self, event_id: int) -> list[SignRetrieve]:
        sign_objs = await self.sign_repository.get_by_event(event_id)
        return [SignRetrieve(sign) for sign in sign_objs]
    
    async def create(self, event_id: int, user_id: int, status: str,) -> SignRetrieve:
        sign_obj = await self.sign_repository.create(user_id, event_id, status)
        return SignRetrieve(sign_obj)
    
    async def update(self, sign_id: int, sign: dict(), user_id: int) -> SignRetrieve | None:
        sign_obj = await self.sign_repository.update(sign_id, sign, user_id)
        return SignRetrieve(sign_obj)
    
    async def delete(self, sign_id: int, user_id: int) -> bool:
        if await self.sign_repository.delete(sign_id, user_id):
            return True
        else:
            return False
        

class CommentaryService:
    def __init__(self, session: AsyncSession) -> None:
        self.commentary_repository = CommentaryRepository(session)
        
    async def get_from_event(self, event_id: int) -> list[CommentaryBase]:
        commentary_objs = await self.commentary_repository.get_from_event(event_id)
        return [CommentaryBase(commentary) for commentary in commentary_objs]
    
    async def create(self, event_id: int, commentary: dict, user_id: int) -> CommentaryBase:
        commentary_obj = await self.commentary_repository.create(event_id, commentary, user_id)
        return CommentaryBase(commentary_obj)
    
    async def update(self, commentary_id: int, commentary: dict, user_id: int) -> CommentaryBase:
        commentary_obj = await self.commentary_repository.update(commentary_id, commentary, user_id)
        return CommentaryBase(commentary_obj)
    
    async def delete(self, commentary_id: int, user_id: int) -> bool:
        if await self.commentary_repository.delete(commentary_id, user_id):
            return True
        else:
            return False
        
        
class LikeService:
    def __init__(self, session: AsyncSession) -> None:
        self.like_repository = LikeRepository(session)
        
    async def get_by_user_id(self, user_id: int) -> list[LikeBase]:
        like_objs = await self.like_repository.get_by_user_id(user_id)
        return [LikeBase(like) for like in like_objs]
    
    async def get_from_event(self, event_id: int) -> list[LikeBase]:
        like_objs = await self.like_repository.get_from_event(event_id)
        return [LikeBase(like) for like in like_objs]
    
    async def create(self, event_id: int, user_id: int) -> LikeBase:
        like_obj = await self.like_repository.create(event_id, user_id)
        return LikeBase(like_obj)
    
    async def delete(self, like_id: int, user_id: int) -> bool:
        if await self.like_repository.delete(like_id, user_id):
            return True
        else:
            return False
        