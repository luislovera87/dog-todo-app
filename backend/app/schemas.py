from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum as PyEnum

class PriorityEnum(str, PyEnum):
    low = "low"
    medium = "medium"
    high = "high"

class TodoCreate(BaseModel):
    task_name: str = Field(..., min_length=1)
    dog_name: str = Field(..., min_length=1)
    description: Optional[str] = None
    priority: PriorityEnum = PriorityEnum.medium
    due_date: Optional[datetime] = None

class TodoUpdate(BaseModel):
    task_name: Optional[str] = None
    dog_name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None

class TodoResponse(BaseModel):
    id: int
    task_name: str
    dog_name: str
    description: Optional[str]
    completed: bool
    priority: PriorityEnum
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    user_id: int

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
