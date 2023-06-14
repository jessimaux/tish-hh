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
        self.event_repository = EventRepository(session)
        self.sign_repository = SignRepository(session)
        self.tag_repository = TagRepository(session)
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

        for tag in event.tags:
            tag_obj = await self.tag_repository.get(tag.name)
            if not tag_obj:
                tag_obj = await self.tag_repository.create(tag.name)
            await self.tag_repository.link_to_event(tag_obj.id, event_obj.id)

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


class TagService:
    def __init__(self, session) -> None:
        self.tag_repository = TagRepository(session)

    async def get_all(self) -> list[TagBase]:
        tag_objs = await self.tag_repository.get_all()
        return [TagBase(tag) for tag in tag_objs]
