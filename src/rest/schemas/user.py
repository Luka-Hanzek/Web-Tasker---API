from pydantic import BaseModel
from typing import List

from enum import Enum


class Role(Enum):
    ADMIN = 1
    BASIC = 2


class UserBase(BaseModel):
    username: str
    email: str
    age: int
    role: Role


class UserCreate(UserBase):
    password: str


class User(UserBase):
    project_ids: List[int]

    class Config:
        orm_mode = True
