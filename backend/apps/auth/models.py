from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship

from database import Base
from apps.events.models import Sign


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(255), unique=True)
    password = Column(String(255))
    
    first_name = Column(String(255))
    last_name = Column(String(255))
    country = Column(String(255))
    region = Column(String(255))
    city = Column(String(255))
    age = Column(Integer)
    
    events = relationship('Event', secondary="events__signs", back_populates='users')
    
    is_verifed = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    
    
class Link(Base):
    __tablename__ = "users__links"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    link = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", backref="links")