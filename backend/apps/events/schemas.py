from pydantic import BaseModel, Field
from datetime import datetime


class CategoryBase(BaseModel):
    id: int | None
    name: str
    
    class Config:
        orm_mode = True
        

class CategoryRetrieve(CategoryBase):
    events_count: int
        

class CharacteristicBase(BaseModel):
    id: int | None
    name: str
    
    class Config:
        orm_mode = True
        
                
class CharacteristicEventBase(BaseModel):
    id: int | None
    description: str
    characteristic: CharacteristicBase
    
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
    id: int | None
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
    characteristics_description: list[CharacteristicEventBase]
    qas: list[QABase]
    images: list[int] | None = Field(..., max_items=10)


class EventRetrieve(EventCreate):
    category: CategoryBase


class SignBase(BaseModel):
    id: int | None
    status: str
    
    class Config:
        orm_mode = True
        
        
class SignRetrieve(SignBase):
    event_id: int
    user_id: int
    
    
class CommentaryBase(BaseModel):
    id: int | None
    content: str
    

class LikeBase(BaseModel):
    id: int | None
    event: EventRetrieve
    created_at: datetime