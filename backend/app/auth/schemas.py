from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str
    email: str
    
    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str
    

class User(UserBase):
    phone: str | None
    first_name: str | None
    last_name: str | None
    country: str | None
    region: str | None
    city: str | None
    age: str | None
        
    
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None