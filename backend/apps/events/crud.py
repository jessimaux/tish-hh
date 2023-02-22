from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from .models import *
from .schemas import *
import crud


async def get_category_or_404(session: AsyncSession, category_name: str | None = None):
    if category_name:
        category = (await session.execute(select(Category).where(Category.name == category_name))).scalar()
    if category:
        return category
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User doesnt exist')


async def get_event(id: int, session: AsyncSession):
    return (await session.execute(select(Event)
                                  .where(Event.id == id)
                                  .options(selectinload(Event.links),
                                           selectinload(Event.characteristics),
                                           selectinload(Event.contacts),
                                           selectinload(Event.qas),
                                           selectinload(Event.tags),
                                           selectinload(Event.category)))).scalar()


async def create_event(event: EventCreate, session: AsyncSession):
    event_obj = Event()
    for attr, value in event:
        if attr in ['tags', 'characteristics', 'links', 'contacts', 'qas']:
            continue
        setattr(event_obj, attr, value)

    for tag in event.tags:
        # check if tag already in
        if tag.name in [t.name for t in event_obj.tags]:
            continue
        # check if tag exist, add or create it
        else:
            tag_obj = (await session.execute(select(Tag)
                                            .where(Tag.name == tag.name))).scalar()
            if not tag_obj:
                tag_obj = Tag(name=tag.name)
                session.add(tag_obj)
            event_obj.tags.append(tag_obj)
            
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


async def edit_event(event: EventCreate, event_obj: Event, session: AsyncSession):
    for attr, value in event:
        if attr not in ['tags', 'dates', 'characteristics', 'links', 'contacts', 'qas']:
            setattr(event_obj, attr, value)

    # add tags for event
    for tag in event.tags:
        if tag.name not in [tag_obj.name for tag_obj in event_obj.tags]:
            tag_obj = (await session.execute(select(Tag)
                                             .where(Tag.name == tag.name))).scalar()
            if not tag_obj:
                tag_obj = Tag(name=tag.name)
                session.add(tag_obj)
            event_obj.tags.append(tag_obj)
            
    # delete tags of event if it doesnt in request        
    for tag_obj in event_obj.tags:
        if tag_obj.name not in [tag.name for tag in event.tags]:
            event_obj.tags.remove(tag_obj)
            
    await crud.update_fg(event_obj.characteristics, Characteristic, event.characteristics, session)
    await crud.update_fg(event_obj.links, EventLink, event.links, session)
    await crud.update_fg(event_obj.contacts, Contact, event.contacts, session)
    await crud.update_fg(event_obj.qas, QA, event.qas, session)

    await session.commit()
    return event_obj
