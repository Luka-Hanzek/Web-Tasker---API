from pydantic import BaseModel
from typing import Optional, List

from enum import Enum, auto


class ProjectVisibility(Enum):
    PRIVATE = 'private'
    PUBLIC = 'public'


class _ProjectBase(BaseModel):
    name: str
    description: str
    visibility: ProjectVisibility


class ProjectGet(_ProjectBase):
    id: int
    owner_username: str
    task_ids: List[int]

    class Config:
        orm_mode = True


class ProjectCreate(_ProjectBase):
    pass
