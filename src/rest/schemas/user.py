from pydantic import BaseModel
from typing import List, Optional

from enum import Enum


class Role(Enum):
    ADMIN = 'admin'
    BASIC = 'basic'


class _UserIdentity(BaseModel):
    username: str


class _UserInfo(BaseModel):
    email: str
    bio: str


class _UserRole(BaseModel):
    role: Role


class _UserAuth(BaseModel):
    password: str


class _UserData(BaseModel):
    project_ids: List[int]
    task_ids: List[int]


class User(_UserIdentity, _UserRole, _UserInfo):
    pass


class UserCreate(_UserIdentity, _UserRole, _UserInfo):
    password: str


class UserUpdateRole(_UserRole):
    pass


class UserUpdatePassword(_UserAuth):
    pass


class UserUpdateInfo(_UserInfo):
    email: Optional[str]
    bio: Optional[str]


class UserGet(_UserIdentity, _UserInfo, _UserRole, _UserData):
    pass

    class Config:
        orm_mode = True

class UserGetIdentity(_UserIdentity):
    class Config:
        orm_mode = True
