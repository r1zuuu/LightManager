from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SwitchCreate(BaseModel):
    name: str

class SwitchUpdate(BaseModel):
    is_on: bool

class SwitchResponse(BaseModel):
    id: str
    name: str
    is_on: bool
    total_time_seconds: float
    last_turned_on: Optional[datetime]

    class Config:
        orm_mode = True
        from_attributes = True
