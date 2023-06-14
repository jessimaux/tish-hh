from pydantic import BaseModel, EmailStr

# TODO: rename, its RT
class Token(BaseModel):
    token: str
    
    
class TokenPare(BaseModel):
    access_token: str
    refresh_token: str


class TokenData(BaseModel):
    username: str = None
    scopes: list[str] = []
    exp: int = None
    