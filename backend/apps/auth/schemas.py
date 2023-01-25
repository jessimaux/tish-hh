from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: str
    
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
    refresh_token: str


class TokenData(BaseModel):
    sub: str = None
    exp: int = None