from pydantic import BaseModel
from typing import Optional

import datetime
from enum import Enum, auto


class Task(BaseModel):
    id: int
    description: str
    start_timestamp: Optional[datetime.datetime]
    end_timestamp: Optional[datetime.date]
    project_id: int
    owner_username: str

    class Config:
        orm_mode = True
