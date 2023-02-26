import os

from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

import crud
import settings
from apps.core.models import Image
from .models import *
from .schemas import *


async def get_category_or_404(session: AsyncSession, category_name: str):
    category = (await session.execute(select(Category)
                                      .where(Category.name == category_name))).scalar()
    if category:
        return category
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Category doesnt exist')


async def get_event(id: int, session: AsyncSession):
    return (await session.execute(select(Event)
                                  .where(Event.id == id)
                                  .options(selectinload(Event.links),
                                           selectinload(Event.characteristics),
                                           selectinload(Event.contacts),
                                           selectinload(Event.qas),
                                           selectinload(Event.tags),
                                           selectinload(Event.category),
                                           selectinload(Event.images)))).scalar()


async def event_tags_update(event: EventCreate, event_obj: Event, session: AsyncSession):
    # remove duplicate and add tag with exists checkout
    tags_map = set([tag.name for tag in event.tags])
    tags_db = [tag_obj.name for tag_obj in event_obj.tags]
    for tag in tags_map:
        if tag.name not in tags_db:
            tag_obj = (await session.execute(select(Tag)
                                             .where(Tag.name == tag.name))).scalar()
            if not tag_obj:
                tag_obj = Tag(name=tag.name)
                session.add(tag_obj)
            event_obj.tags.append(tag_obj)

    # delete tags of event if it doesnt in request
    for tag_obj in event_obj.tags:
        if tag_obj.name not in tags_map:
            event_obj.tags.remove(tag_obj)
            

async def create_event(event: EventCreate, session: AsyncSession):
    event_obj = Event()
    for attr, value in event:
        if attr in ['tags', 'characteristics', 'links', 'contacts', 'qas', 'images']:
            continue
        setattr(event_obj, attr, value)

    # remove duplicate and add tag with exists checkout
    tags_map = set([tag.name for tag in event.tags])
    for tag_name in tags_map:
        tag_obj = (await session.execute(select(Tag)
                                         .where(Tag.name == tag_name))).scalar()
        if not tag_obj:
            tag_obj = Tag(name=tag_name)
            session.add(tag_obj)
        event_obj.tags.append(tag_obj)

    for characteristic in event.characteristics:
        event_obj.characteristics.append(Characteristic(name=characteristic.name,
                                                        description=characteristic.description))
    for link in event.links:
        event_obj.links.append(EventLink(name=link.name,
                                         link=link.link))
    for contact in event.contacts:
        event_obj.contacts.append(Contact(name=contact.name,
                                          description=contact.description,
                                          contact=contact.contact))
    for qa in event.qas:
        event_obj.qas.append(QA(quest=qa.quest,
                                answer=qa.answer))
        
    session.add(event_obj)
    await session.flush()
    
    # update generic fg key to link with created event
    image_objs = (await session.execute(select(Image)
                                        .where(Image.id.in_(event.images)))).scalars().all()
    for image_obj in image_objs:
        image_obj.object_type = 'Event'
        image_obj.object_id = event_obj.id
    
    await session.commit()
    return event_obj


async def edit_event(event: EventCreate, event_obj: Event, session: AsyncSession):
    for attr, value in event:
        if attr not in ['tags', 'dates', 'characteristics', 'links', 'contacts', 'qas', 'images']:
            setattr(event_obj, attr, value)
    await crud.update_fg(event_obj.characteristics, Characteristic, event.characteristics, session)
    await crud.update_fg(event_obj.links, EventLink, event.links, session)
    await crud.update_fg(event_obj.contacts, Contact, event.contacts, session)
    await crud.update_fg(event_obj.qas, QA, event.qas, session)
    await event_tags_update(event, event_obj, session)
    # Delete image from server/db if that doesnt exist in request
    imgs_id_request = [img.id for img in event.images] 
    for img_obj in event_obj.images:
        if img_obj.id not in imgs_id_request:
            file_path = os.path.join(settings.BASEDIR, img_obj.image[1:])
            if os.path.exists(file_path):
                os.remove(file_path)
            event_obj.images.remove(img_obj)
    await session.commit()
    return event_obj
