from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete='CASCADE'))
    category = relationship("Category", backref="events")
    
    date = Column(DateTime(timezone=True))
    
    country = Column(String(255), nullable=True)
    region = Column(String(255), nullable=True)
    city = Column(String(255), nullable=True)
    
    is_private = Column(Boolean)
    is_closed = Column(Boolean)
    
    signs = relationship('Sign', back_populates='event', lazy='dynamic')
    tags = relationship('Tag', secondary="events__tags", back_populates="events")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    
class Characteristic(Base):
    __tablename__ = "events__characteristics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(String(255))
    event_id = Column(Integer, ForeignKey("events.id", ondelete='CASCADE'))
    
    event = relationship("Event", backref="characteristics")
    
class EventLink(Base):
    __tablename__ = "events__links"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    link = Column(String)
    event_id = Column(Integer, ForeignKey("events.id", ondelete='CASCADE'))
    
    event = relationship("Event", backref="links")
    
class Contact(Base):
    __tablename__ = "events__contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(String(255))
    contact = Column(String(255))
    event_id = Column(Integer, ForeignKey("events.id", ondelete='CASCADE'))
    
    event = relationship("Event", backref="contacts")
    
class QA(Base):
    __tablename__ = "events__qa"
    
    id = Column(Integer, primary_key=True, index=True)
    quest = Column(String(255))
    answer = Column(String(255))
    event_id = Column(Integer, ForeignKey("events.id", ondelete='CASCADE'))

    event = relationship("Event", backref="qas")

    
class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True)
    
    events = relationship("Event", secondary="events__tags", back_populates="tags")


class TagEvent(Base):
    __tablename__ = "events__tags"
    
    event_id = Column(Integer, ForeignKey("events.id", ondelete='CASCADE'), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete='CASCADE'), primary_key=True)
    
    
class Sign(Base):
    __tablename__ = "events__signs"

    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete='CASCADE'), primary_key=True)
    status = Column(String(255))
    
    user = relationship("User", back_populates="signs")
    event = relationship("Event", back_populates="signs")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    