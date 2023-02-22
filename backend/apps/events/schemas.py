from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal


class CategoryBase(BaseModel):
    id: int | None
    name: str
    
    class Config:
        orm_mode = True
        

class CharacteristicBase(BaseModel):
    id: int | None
    name: str
    description: str
    
    class Config:
        orm_mode = True
        

class LinkBase(BaseModel):
    id: int | None
    name: str
    link: str
    
    class Config:
        orm_mode = True
        

class ContactBase(BaseModel):
    id: int | None
    name: str
    description: str
    contact: str
    
    class Config:
        orm_mode = True
        
        
class QABase(BaseModel):
    id: int | None
    quest: str
    answer: str
    
    class Config:
        orm_mode = True

        
class TagBase(BaseModel):
    id: int | None
    name: str
    
    class Config:
        orm_mode = True
        

class EventBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str
    
    country: str | None
    region: str | None
    city: str | None
    
    is_private: bool
    is_closed: bool
    
    class Config:
        orm_mode = True
        

class EventCreate(EventBase):
    category_id: int
    tags: list[TagBase]
    links: list[LinkBase]
    contacts: list[ContactBase]
    characteristics: list[CharacteristicBase]
    qas: list[QABase]


class EventRetrieve(EventBase):
    id: int
    category: CategoryBase
    tags: list[TagBase]
    links: list[LinkBase]
    contacts: list[ContactBase]
    characteristics: list[CharacteristicBase]
    qas: list[QABase]


class SignBase(BaseModel):
    status: str
    event_id: int
    
    class Config:
        orm_mode = True
        
        
class SignRetrieve(SignBase):
    id: int
    user_id: int