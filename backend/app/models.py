from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from app.database import Base
from enum import Enum as PyEnum

class PriorityEnum(str, PyEnum):
    low = "low"
    medium = "medium"
    high = "high"

class TodoItem(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String, nullable=False)
    dog_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.medium)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
