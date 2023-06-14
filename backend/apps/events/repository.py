from sqlalchemy import select, func, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .models import *


class EventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, event_id: int) -> Event:
        return (await self.session.execute(select(Event)
                                           .where(Event.id == event_id))).scalar()

    async def get_all(self) -> list[Event]:
        return (await self.session.execute(select(Event))).scalars().all()

    async def get_from_category(self, category_name: str) -> list[Event]:
        subquery_category = (select(Category.id)
                             .where(Category.name == category_name)
                             .subquery())
        return (await self.session.execute(select(Event)
                                           .where(Event.category_id == subquery_category))).scalars().all()

    async def create(self, event: dict) -> Event:
        return (await self.session.execute(insert(Event)
                                           .values(**event)
                                           .returning(Event))).scalar()


class SignRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user_id: int, event_id: int, role: str) -> Sign | None:
        sign_obj = (await self.session.execute(insert(Sign)
                                               .values(user_id=user_id,
                                                       event_id=event_id,
                                                       role=role)
                                               .returning(Sign))).scalar()
        await self.session.commit()
        return sign_obj


class CategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all_with_meta(self):
        return await self.session.execute(select(Category.id, Category.name, func.count(Event.id).label('events_count'))
                                          .join(Event, Category.id == Event.category_id, isouter=True)
                                          .group_by(Category.id)
                                          .order_by(func.count(Event.id).desc()))


class TagRepository:
    def __init__(self, session: AsyncSession) -> None:
        self. session = session

    async def get_all(self) -> list[Tag]:
        return (await self.session.execute(select(Tag))).scalars().all()

    async def get(self, name: str) -> Tag | None:
        return (await self.session.execute(select(Tag)
                                           .where(Tag.name == name))).scalar()

    async def create(self, name: str) -> Tag | None:
        return (await self.session.execute(insert(Tag)
                                           .values(name=name)
                                           .returning(Tag))).scalar()

    async def link_to_event(self, tag_id: int, event_id: int) -> TagEvent | None:
        return (await self.session.execute(insert(TagEvent)
                                           .values(tag_id=tag_id, event_id=event_id)
                                           .returning(TagEvent))).scalar()


class CharacteristicRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, name: str) -> Characteristic:
        return (await self.session.execute(insert(Characteristic)
                                           .values(name=name)
                                           .returning(Characteristic))).scalar()

    async def link_to_event(self, description: str, characteristic_id: int, event_id: int) -> CharacteristicEvent:
        return (await self.session.execute(insert(CharacteristicEvent)
                                           .values(description=description,
                                                   characteristic_id=characteristic_id,
                                                   event_id=event_id)
                                           .returning(CharacteristicEvent))).scalar()


class QARepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, qa: dict) -> QA:
        return (await self.session.execute(insert(QA)
                                           .values(**qa)
                                           .returning(QA))).scalar()
