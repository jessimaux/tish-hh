from sqlalchemy import Column, Integer, Unicode, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    
    object_type = Column(Unicode(255), nullable=True)
    object_id = Column(Integer, nullable=True)

    user = relationship('User',
                        back_populates='image',
                        primaryjoin="and_(remote(User.id) == foreign(Image.object_id), Image.object_type == 'User')")
    event = relationship('Event',
                        back_populates='images',
                        primaryjoin="and_(remote(Event.id) == foreign(Image.object_id), Image.object_type == 'Event')")
    
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    