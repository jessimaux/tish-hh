from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from .models import *
from .schemas import *
import crud


async def get_event(id: int, session: AsyncSession):
    return (await session.execute(select(Event)
                                  .where(Event.id == id)
                                  .options(selectinload(Event.dates),
                                           selectinload(Event.links),
                                           selectinload(Event.characteristics),
                                           selectinload(Event.contacts),
                                           selectinload(Event.qas),
                                           selectinload(Event.tags),
                                           selectinload(Event.category)))).scalar()


async def create_event(event: EventCreate, session: AsyncSession):
    event_obj = Event()
    for attr, value in event:
        if attr in ['tags', 'dates', 'characteristics', 'links', 'contacts', 'qas']:
            continue
        setattr(event_obj, attr, value)

    for tag in event.tags:
        tag_obj = (await session.execute(select(Tag)
                                         .where(Tag.name == tag.name))).scalar()
        event_obj.tags.append(tag_obj)

    for date in event.dates:
        event_obj.dates.append(Date(date=date.date))

    for characteristic in event.characteristics:
        event_obj.characteristics.append(Characteristic(name=characteristic.name,
                                                        description=characteristic.description,
                                                        event_id=event_obj.id))

    for link in event.links:
        event_obj.links.append(EventLink(name=link.name,
                                         link=link.link,
                                         event_id=event_obj.id))

    for contact in event.contacts:
        event_obj.contacts.append(Contact(name=contact.name,
                                          description=contact.description,
                                          contact=contact.contact,
                                          event_id=event_obj.id))

    for qa in event.qas:
        event_obj.qas.append(QA(quest=qa.quest,
                                answer=qa.answer,
                                event_id=event_obj.id))

    session.add(event_obj)
    await session.commit()
    return event_obj


async def edit_event(id: int, event: EventCreate, session: AsyncSession):
    event_obj = await get_event(id, session)
    for attr, value in event:
        if attr not in ['tags', 'dates', 'characteristics', 'links', 'contacts', 'qas']:
            setattr(event_obj, attr, value)

    for tag_id in event.tags:
        if tag_id not in [tag_obj.id for tag_obj in event_obj.tags]:
            tag_obj = (await session.execute(select(Tag)
                                             .where(Tag.id == tag_id))).scalar()
            event_obj.tags.append(tag_obj)
            
    for tag_obj in event_obj.tags:
        if tag_obj.id not in event.tags:
            event_obj.tags.remove(tag_obj)
            
    await crud.update_fg(event_obj.dates, Date, event.dates, session)
    await crud.update_fg(event_obj.characteristics, Characteristic, event.characteristics, session)
    await crud.update_fg(event_obj.links, EventLink, event.links, session)
    await crud.update_fg(event_obj.contacts, Contact, event.contacts, session)
    await crud.update_fg(event_obj.qas, QA, event.qas, session)

    await session.commit()
    return event_obj
