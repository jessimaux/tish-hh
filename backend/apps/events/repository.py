from sqlalchemy import select, func, insert, delete, update
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

    async def update(self, event: dict, user_id: int) -> Event:
        obj = (await self.session.execute(update(Event)
                                          .where(Event.id == event.id,
                                                 Event.created_by == user_id)
                                          .values(**event)
                                          .returning(Event))).scalar()
        await self.session.commit()
        return obj
    
    async def delete(self, event_id: int, user_id: int) -> int:
        result = (await self.session.execute(delete(Event)
                                             .where(Event.id == event_id,
                                                    Event.created_by == user_id))).rowcount
        await self.session.commit()
        return result


class SignRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        
    async def get(self, sign_id: int) -> Sign | None:
        return (await self.session.execute(select(Sign)
                                           .where(Sign.id == sign_id))).scalar()
        
    async def get_by_event(self, event_id: int) -> Sign | None:
        return (await self.session.execute(select(Sign)
                                           .where(Sign.event_id == event_id))).scalars().all()

    async def create(self, user_id: int, event_id: int, role: str) -> Sign | None:
        sign_obj = (await self.session.execute(insert(Sign)
                                               .values(user_id=user_id,
                                                       event_id=event_id,
                                                       role=role)
                                               .returning(Sign))).scalar()
        await self.session.commit()
        return sign_obj
    
    async def update(self, sign_id: int, sign: dict, user_id: int) -> Sign | None:
        obj = (await self.session.execute(update(Sign)
                                          .where(Sign.id == sign_id,
                                                 Sign.user_id == user_id)
                                          .values(**sign)
                                          .returning(Sign))).scalar()
        await self.session.commit()
        return obj
    
    async def delete(self, sign_id: int, user_id: int) -> int:
        result = (await self.session.execute(delete(Sign)
                                             .where(Sign.id == sign_id,
                                                    Sign.user_id == user_id))).rowcount
        await self.session.commit()
        return result


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

    async def get_by_event(self, event_id: int) -> list[Tag] | None:
        return (await self.session.execute(select(Tag)
                                           .join(TagEvent, TagEvent.tag_id == Tag.id)
                                           .where(TagEvent.event_id == event_id))).scalars().all()

    async def create(self, name: str) -> Tag | None:
        return (await self.session.execute(insert(Tag)
                                           .values(name=name)
                                           .returning(Tag))).scalar()

    async def link_to_event(self, tag_id: int, event_id: int) -> TagEvent | None:
        return (await self.session.execute(insert(TagEvent)
                                           .values(tag_id=tag_id, event_id=event_id)
                                           .returning(TagEvent))).scalar()

    async def unlink_to_event(self, tag_id: int, event_id: int) -> int:
        result = (await self.session.execute(delete(TagEvent)
                                             .where(event_id=event_id,
                                                    tag_id=tag_id))).rowcount
        await self.session.commit()
        return result


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


class CommentaryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        
    async def get_from_event(self, event_id: int) -> Commentary | None:
        return (await self.session.execute(select(Commentary)
                                           .where(Commentary.event_id == event_id))).scalars().all()
        
    async def create(self, event_id: int, commentary: dict, user_id: int) -> Commentary | None:
        return (await self.session.execute(insert(Commentary)
                                           .values(event_id=event_id, created_by=user_id, **commentary)
                                           .returning(Commentary))).scalar()
        
    async def update(self, commentary_id: int, commentary: dict, user_id: int) -> Commentary | None:
        obj = (await self.session.execute(update(Commentary)
                                          .where(Commentary.id == commentary_id,
                                                 Commentary.created_by == user_id)
                                          .values(**commentary)
                                          .returning(Commentary))).scalar()
        await self.session.commit()
        return obj
    
    async def delete(self, commentary_id: int, user_id: int) -> int:
        result = (await self.session.execute(delete(Commentary)
                                             .where(Commentary.id == commentary_id,
                                                    Commentary.created_by == user_id))).rowcount
        await self.session.commit()
        return result
    
    
class LikeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        
    async def get_by_user_id(self, user_id: int) -> list[Like]:
        return (await self.session.execute(select(Like)
                                           .where(Like.user_id == user_id))).scalars().all()
        
    async def get_from_event(self, event_id: int) -> list[Like]:
        return (await self.session.execute(select(Like)
                                           .where(Like.event_id == event_id))).scalars().all()
        
    async def create(self, event_id: int, user_id: int) -> Like | None:
        return (await self.session.execute(insert(Like)
                                           .values(event_id=event_id, user_id=user_id)
                                           .returning(Like))).scalar()
        
    async def delete(self, like_id: int, user_id: int) -> int:
        result = (await self.session.execute(delete(Like)
                                             .where(Like.id == like_id))).rowcount
        await self.session.commit()
        return result