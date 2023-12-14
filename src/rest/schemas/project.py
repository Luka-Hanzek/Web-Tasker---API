from pydantic import BaseModel
from typing import Optional, List

from enum import Enum, auto


class ProjectVisibility(Enum):
    PRIVATE = 'private'
    PUBLIC = 'public'


class _ProjectIdentity(BaseModel):
    id: int


class _ProjectInfo(BaseModel):
    name: str
    description: str
    visibility: ProjectVisibility


class _ProjectTasks(BaseModel):
    task_ids: List[int]


class _ProjectOwner(BaseModel):
    owner_username: str


class ProjectGet(_ProjectIdentity, _ProjectInfo, _ProjectTasks, _ProjectOwner):
    class Config:
        orm_mode = True


class ProjectCreate(_ProjectInfo):
    pass
