from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    token: str
    
    
class TokenPare(BaseModel):
    access_token: str
    refresh_token: str


class TokenData(BaseModel):
    email: str = None
    scopes: list[str] = []
    exp: int = None
    
