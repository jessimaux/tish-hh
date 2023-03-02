from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    id: int | None
    name: str
    
    class Config:
        orm_mode = True
        

class CategoryRetrieve(CategoryBase):
    events_count: int
        

class ImageBase(BaseModel):
    id: int | None
    image: str
    
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
    links: list[LinkBase]
    contacts: list[ContactBase]
    characteristics: list[CharacteristicBase]
    qas: list[QABase]
    images: list[int] | None = Field(..., max_items=10)


class EventRetrieve(EventCreate):
    category: CategoryBase


class SignBase(BaseModel):
    status: str
    event_id: int
    
    class Config:
        orm_mode = True
        
        
class SignRetrieve(SignBase):
    id: int
    user_id: int