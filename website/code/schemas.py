from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class Token(BaseModel):
    accessToken: str
    tokenType: str

class TokenData(BaseModel):
    email: Optional[str] = None