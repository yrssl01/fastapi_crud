from pydantic import EmailStr, BaseModel


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    # created_at: datetime

    class Config:
        from_attributes = True