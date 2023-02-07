from pydantic import BaseModel, EmailStr


class LinkBase(BaseModel):
    name: str
    link: str
    
    class Config:
        orm_mode = True
        
        
class UserBase(BaseModel):
    email: str
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
    country: str
    region: str
    city: str
    age: int | None
    gender: bool | None
    bio: str | None
    links: list[LinkBase] | list
    
    
class UserRetrieve(UserUpdate):
    id: int
    image: str | None
    
    
class Token(BaseModel):
    access_token: str
    refresh_token: str


class TokenData(BaseModel):
    email: str = None
    exp: int = None