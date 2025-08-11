from datetime import datetime
from pydantic import BaseModel, Field
from src.schemas.users import UserOut


class PostBase(BaseModel):
    title: str = Field(max_length=100)
    content: str = Field(max_length=2000)
    published: bool = True


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    class Config:
        from_attributes = True



class PostOut(BaseModel):
    Post: Post
    votes: int

    class Config:
        from_attributes = True


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    
    class Config:
        from_attributes = True