from pydantic import BaseModel
from typing import Optional

import datetime


class _TaskIdentity(BaseModel):
    id: int


class _TaskInfo(BaseModel):
    project_id: int
    description: str
    owner_username: str


class _TaskData(BaseModel):
    start_timestamp: Optional[datetime.datetime]
    end_timestamp: Optional[datetime.date]


class TaskCreate(_TaskInfo):
    pass


class TaskGet(_TaskIdentity, _TaskInfo, _TaskData):
    class Config:
        orm_mode = True
