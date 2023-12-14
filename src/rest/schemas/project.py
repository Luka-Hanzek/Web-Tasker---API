from pydantic import BaseModel
from typing import Optional, List

from enum import Enum, auto


class ProjectVisibility(Enum):
    PRIVATE = 'private'
    PUBLIC = 'public'


class ProjectBase(BaseModel):
    name: str
    owner_username: str
    description: str
    visibility: ProjectVisibility
    task_ids: List[int]


class ProjectGet(ProjectBase):
    id: int

    class Config:
        orm_mode = True


class ProjectCreate(BaseModel):
    pass
