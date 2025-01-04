from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        ormMode = True

class Token(BaseModel):
    accessToken: str
    tokenType: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ChatBase(BaseModel):
    name: str

class ChatCreate(ChatBase):
    pass

class ChatResponse(ChatBase):
    id: int
    ownerId: int

    class Config:
        fromAttrubutes = True