from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str
    
    class Config:
        orm_mode = True
        
        
class TagBase(BaseModel):
    name: str
    
    class Config:
        orm_mode = True