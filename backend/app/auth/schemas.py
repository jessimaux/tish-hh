from pydantic import BaseModel, Field


class UserBase(BaseModel):
    email: str
    
    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str
    

class User(UserBase):
    username: str | None
    phone: str | None
    first_name: str | None
    last_name: str | None
    country: str | None
    region: str | None
    city: str | None
    age: str | None
        
    
class Token(BaseModel):
    access_token: str
    refresh_token: str


class TokenData(BaseModel):
    sub: str = None
    exp: int = None