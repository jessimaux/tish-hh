from pydantic import BaseModel


class ImageBase(BaseModel):
    id: int | None
    url: str
    
    class Config:
        orm_mode = True