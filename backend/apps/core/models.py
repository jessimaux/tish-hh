from sqlalchemy import Column, Integer, Unicode, String, ForeignKey, DateTime, and_, text,  func
from sqlalchemy.orm import relationship

from database import Base
from apps.users.models import User
from apps.events.models import Event


class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    client = Column(String(255))
    refresh_token = Column(String(255))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship('User', backref='sessions')


class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    
    # This is used to discriminate between the linked tables.
    object_type = Column(Unicode(255), nullable=True)
    # This is used to point to the primary key of the linked row.
    object_id = Column(Integer, nullable=True)

    user = relationship('User',
                        back_populates='image',
                        primaryjoin="and_(remote(User.id) == foreign(Image.object_id), Image.object_type == 'User')")
    event = relationship('Event',
                        back_populates='images',
                        primaryjoin="and_(remote(Event.id) == foreign(Image.object_id), Image.object_type == 'Event')")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    
class Notification(Base):
    __tablename__ = 'notification'
    
    id = Column(Integer, primary_key=True, index=True)
    notification_type_id = Column(Integer, ForeignKey("notification_type.id", ondelete='CASCADE'))
    object_type = Column(String(255))
    object_id = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    

class NotificationType(Base):
    __tablename__ = 'notification_type'
    
    id = Column(Integer, primary_key=True, index=True)
    template = Column(String)
    description = Column(String(255))
    

class NotificationSender(Base):
    __tablename__ = 'notification_sender'
    
    id = Column(Integer, primary_key=True, index=True)
    triger_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    notifier_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    notification_id = Column(Integer, ForeignKey('notification.id'))