from pydantic import BaseModel
from typing import Optional

import datetime


class _TaskIdentity(BaseModel):
    id: int


class _TaskProject(BaseModel):
    project_id: int


class _TaskInfo(BaseModel):
    description: str


class _TaskOwner(BaseModel):
    owner_username: str


class _TaskOwner(BaseModel):
    owner_username: str


class _TaskTime(BaseModel):
    start_timestamp: Optional[datetime.datetime]
    end_timestamp: Optional[datetime.date]


class TaskCreate(_TaskInfo):
    pass


class TaskGet(_TaskIdentity, _TaskProject, _TaskInfo, _TaskOwner, _TaskTime):
    class Config:
        orm_mode = True


class TaskUpdate(_TaskInfo):
    description: Optional[str] = None
