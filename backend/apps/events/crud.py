from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import *
from .schemas import *


async def create_event(event: EventCreate, session: AsyncSession):
    event_obj = Event()
    for attr, value in event:
        if attr in ['tags', 'dates', 'characteristics', 'links', 'contacts', 'qas']:
            continue
        setattr(event_obj, attr, value)

    # for m2m event-tags
    for tag in event.tags:
        tag_res = await session.execute(select(Tag).where(Tag.name == tag.name))
        tag_db = tag_res.scalar()
        event_obj.tags.append(tag_db)

    # for fg dates
    for date in event.dates:
        event_obj.dates.append(Date(date=date.date))

    # for fg characteristics
    for characteristic in event.characteristics:
        event_obj.characteristics.append(Characteristic(name=characteristic.name,
                                                        description=characteristic.description,
                                                        event_id=event_obj.id))
    # for fg links
    for link in event.links:
        event_obj.links.append(Link(name=link.name,
                                    link=link.link,
                                    event_id=event_obj.id))
    # for fg contacts
    for contact in event.contacts:
        event_obj.contacts.append(Contact(name=contact.name,
                                          description=contact.description,
                                          contact=contact.contact,
                                          event_id=event_obj.id))
    # for fg QAs
    for qa in event.qas:
        event_obj.qas.append(QA(quest=qa.quest,
                                answer=qa.answer,
                                event_id=event_obj.id))

    session.add(event_obj)
    await session.commit()
    return event_obj


async def edit_event(id: int, event: EventCreate, session: AsyncSession):
    event_res = await session.execute(select(Event).where(Event.id == id))
    event_obj = event_res.scalar()
    for attr, value in event:
        if attr in ['tags', 'dates', 'characteristics', 'links', 'contacts', 'qas']:
            continue
        setattr(event_obj, attr, value)

    # for m2m event-tags
    tags = list()
    for tag in event.tags:
        tag_res = await session.execute(select(Tag).where(Tag.name == tag.name))
        tag_db = tag_res.scalar()
        tags.append(tag_db)
    event_obj.tags = tags

    # for fg dates
    dates = list()
    for date in event.dates:
        dates.append(Date(date=date.date))
    event_obj.dates = dates

    # for fg characteristics
    characteristics = list()
    for characteristic in event.characteristics:
        characteristics.append(Characteristic(name=characteristic.name,
                                              description=characteristic.description,
                                              event_id=event_obj.id))
    event_obj.characterestics = characteristics

    # for fg links
    links = list()
    for link in event.links:
        links.append(Link(name=link.name,
                          link=link.link,
                          event_id=event_obj.id))
    event_obj.links = links

    # for fg contacts
    contacts = list()
    for contact in event.contacts:
        contacts.append(Contact(name=contact.name,
                                description=contact.description,
                                contact=contact.contact,
                                event_id=event_obj.id))
    event_obj.contacts = contacts

    # for fg QAs
    qas = list()
    for qa in event.qas:
        qas.append(QA(quest=qa.quest,
                      answer=qa.answer,
                      event_id=event_obj.id))
    event_obj.qas = qas

    session.add(event_obj)
    await session.commit()
    return event_obj
