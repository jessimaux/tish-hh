from sqlalchemy_utils import generic_relationship
from sqlalchemy import Column, Integer, Unicode, String, and_, text
from sqlalchemy.orm import relationship, backref

from database import Base
from apps.users.models import User
from apps.events.models import Event


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
    