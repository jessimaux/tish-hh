from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(255), unique=True)
    password = Column(String(255))
    
    name = Column(String(255))
    country = Column(String(255))
    region = Column(String(255))
    city = Column(String(255))
    age = Column(Integer, nullable=True)
    gender = Column(Boolean, nullable=True)
    bio = Column(String(255))
    image = Column(String, nullable=True)
    
    # TODO: maybe backref?
    events = relationship('Sign', back_populates='user')
    
    is_verifed = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    
class Link(Base):
    __tablename__ = "users__links"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    link = Column(String)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    
    user = relationship("User", backref="links")