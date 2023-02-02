from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal

from apps.auth.schemas import UserRetrieve


class CategoryBase(BaseModel):
    name: str
    
    class Config:
        orm_mode = True
        

class DateBase(BaseModel):
    date: datetime
    
    class Config:
        orm_mode = True
        

class CharacteristicBase(BaseModel):
    name: str
    description: str
    
    class Config:
        orm_mode = True
        

class LinkBase(BaseModel):
    name: str
    link: str
    
    class Config:
        orm_mode = True
        

class ContactBase(BaseModel):
    name: str
    description: str
    contact: str
    
    class Config:
        orm_mode = True
        
        
class QABase(BaseModel):
    quest: str
    answer: str
    
    class Config:
        orm_mode = True

        
class TagBase(BaseModel):
    name: str
    
    class Config:
        orm_mode = True
        

class EventBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str
    address: str
    
    category_id: int
    
    repeatable: bool
    repeatable_type: Literal['day', 'week', 'month', 'year']
    
    is_private: bool
    is_closed: bool
    is_template: bool
    is_announcement: bool
    
    class Config:
        orm_mode = True
        

class EventCreate(EventBase):
    tags: list[TagBase]
    links: list[LinkBase]
    contacts: list[ContactBase]
    characteristics: list[CharacteristicBase]
    dates: list[DateBase]
    qas: list[QABase]


class EventRetrieve(EventCreate):
    id: int    


class SignBase(BaseModel):
    status: str
    user_id: int
    event_id: int
    
    class Config:
        orm_mode = True
        
        
class SignRetrieve(SignBase):
    id: int
