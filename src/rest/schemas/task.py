from pydantic import BaseModel
from typing import Optional

import datetime
from enum import Enum, auto


class _TaskBase(BaseModel):
    description: str
    start_timestamp: Optional[datetime.datetime]
    end_timestamp: Optional[datetime.date]
    project_id: int
    owner_username: str


class TaskCreate(_TaskBase):
    id: int


class TaskGet(_TaskBase):
    id: int

    class Config:
        orm_mode = True
