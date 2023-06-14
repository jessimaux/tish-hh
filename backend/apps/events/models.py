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
    
    is_private = Column(Boolean, default=False)
    is_closed = Column(Boolean, default=False)
    
    images = relationship('Image',
                          back_populates='event',
                          primaryjoin="and_(Event.id == foreign(Image.object_id), Image.object_type == 'Event')",
                          lazy='selectin')
    signs = relationship('Sign', back_populates='event', lazy='dynamic')
    tags = relationship('Tag', secondary="events__tags", back_populates="events")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(Integer, ForeignKey("users.id"))
    
        
class Characteristic(Base):
    __tablename__ = "characteristics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    
class CharacteristicEvent(Base):
    __tablename__ = "events__characteristics"
    
    description = Column(String(255))
    
    event_id = Column(Integer, ForeignKey("events.id", ondelete='CASCADE'), primary_key=True)
    characteristic_id = Column(Integer, ForeignKey("characteristics.id", ondelete='CASCADE'), primary_key=True)
    
    event = relationship("Event", back_populates="characteristics_description")
    characteristic = relationship("Characteristic", back_populates="characteristics_description")

    
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
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True)
    
    events = relationship("Event", secondary="events__tags", back_populates="tags")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TagEvent(Base):
    __tablename__ = "events__tags"
    
    event_id = Column(Integer, ForeignKey("events.id", ondelete='CASCADE'), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete='CASCADE'), primary_key=True)
    
    
class Sign(Base):
    __tablename__ = "events__signs"

    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete='CASCADE'), primary_key=True)
    role = Column(String(255))
    status = Column(String(255), nullable=True)
    
    user = relationship("User", back_populates="signs")
    event = relationship("Event", back_populates="signs")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    
class Commentary(Base):
    __tablename__ = "events__commentaries"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    event_id = Column(Integer, ForeignKey("events.id", ondelete='CASCADE'))
    
    event = relationship("Event", backref="commentaries")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(Integer, ForeignKey("users.id"))
    

class Like(Base):
    __tablename__ = "events__likes"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    event = relationship("Event", backref="likes")
    user = relationship("User", backref="likes")