from pydantic import BaseModel
from typing import List

from enum import Enum


class Role(Enum):
    ADMIN = 'admin'
    BASIC = 'basic'


class _UserBase(BaseModel):
    email: str
    age: int
    role: Role


class User(_UserBase):
    username: int


class UserCreate(_UserBase):
    username: str
    password: str


class UserUpdateRole(BaseModel):
    username: str
    role: Role


class UserUpdatePassword(BaseModel):
    username: str
    password: str


class UserGet(_UserBase):
    username: str
    project_ids: List[int]

    class Config:
        orm_mode = True
