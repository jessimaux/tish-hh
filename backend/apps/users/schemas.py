from pydantic import BaseModel, EmailStr

from apps.core.schemas import ImageBase
    

class LinkBase(BaseModel):
    id: int | None
    name: str
    link: str
    
    class Config:
        orm_mode = True
        
        
class UserBase(BaseModel):
    email: EmailStr
    username: str
    
    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str


class UserPasswordChange(BaseModel):
    old_password: str
    new_password: str
        

class UserUpdate(UserBase):
    phone: str | None
    name: str | None
    country: str | None
    region: str | None
    city: str | None
    age: int | None
    gender: bool | None
    bio: str | None
    links: list[LinkBase] | list
    
    
class UserRetrieve(UserUpdate):
    id: int
    image: ImageBase | None
    
    
class UserGet(UserRetrieve):
    events_count: int
    followers_count: int
    following_count: int
    
    
class SubscriptionBase(BaseModel):
    publisher_id: int
    subscriber_id: int
    
    class Config:
        orm_mode = True