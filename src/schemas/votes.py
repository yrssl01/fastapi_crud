from pydantic import BaseModel, Field


class Vote(BaseModel):
    post_id: int
    dir: int = Field(ge=0, le=1)
