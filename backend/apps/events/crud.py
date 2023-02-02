from sqlalchemy.orm import Session

from . import models, schemas


def create_event(event: schemas.EventCreate, db: Session):
    event_obj = models.Event()
    for attr, value in event:
        if attr in ['tags', 'dates', 'characteristics', 'links', 'contacts', 'qas']:
            continue
        setattr(event_obj, attr, value)
    
    # for m2m event-tags
    for tag in event.tags:
        tag_db = db.query(models.Tag).filter(models.Tag.name == tag.name).first()
        event_obj.tags.append(tag_db)
        
    # for fg dates
    for date in event.dates:
        event_obj.dates.append(models.Date(date=date.date))
    
    # for fg characteristics
    for characteristic in event.characteristics:
        event_obj.characteristics.append(models.Characteristic(name=characteristic.name, 
                                                               description=characteristic.description,
                                                               event_id=event_obj.id))
    # for fg links    
    for link in event.links:
        event_obj.links.append(models.Link(name=link.name, 
                                           link=link.link,
                                           event_id=event_obj.id))
    # for fg contacts
    for contact in event.contacts:
        event_obj.contacts.append(models.Contact(name=contact.name, 
                                                 description=contact.description,
                                                 contact=contact.contact,
                                                 event_id=event_obj.id))
    # for fg QAs
    for qa in event.qas:
        event_obj.qas.append(models.QA(quest=qa.quest, 
                                       answer=qa.answer,
                                       event_id=event_obj.id))
        
    db.add(event_obj)
    db.commit()
    return event_obj


def edit_event(id:int, event: schemas.EventCreate, db: Session):
    event_obj = db.query(models.Event).filter(models.Event.id == id).first()
    for attr, value in event:
        if attr in ['tags', 'dates', 'characteristics', 'links', 'contacts', 'qas']:
            continue
        setattr(event_obj, attr, value)
    
    # for m2m event-tags
    tags = list()
    for tag in event.tags:
        tag_db = db.query(models.Tag).filter(models.Tag.name == tag.name).first()
        tags.append(tag_db)
    event_obj.tags = tags
        
    # for fg dates
    dates = list()
    for date in event.dates:
        dates.append(models.Date(date=date.date))
    event_obj.dates = dates
    
    # for fg characteristics
    characteristics = list()
    for characteristic in event.characteristics:
        characteristics.append(models.Characteristic(name=characteristic.name, 
                                                     description=characteristic.description,
                                                     event_id=event_obj.id))
    event_obj.characterestics = characteristics
    
    # for fg links   
    links = list() 
    for link in event.links:
        links.append(models.Link(name=link.name, 
                                 link=link.link,
                                 event_id=event_obj.id))
    event_obj.links = links    
        
    # for fg contacts
    contacts = list()
    for contact in event.contacts:
        contacts.append(models.Contact(name=contact.name, 
                                       description=contact.description,
                                       contact=contact.contact,
                                       event_id=event_obj.id))
    event_obj.contacts = contacts    
        
    # for fg QAs
    qas = list()
    for qa in event.qas:
        qas.append(models.QA(quest=qa.quest, 
                             answer=qa.answer,
                             event_id=event_obj.id))
    event_obj.qas = qas
        
    db.add(event_obj)
    db.commit()
    return event_obj

