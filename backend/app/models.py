from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class Role(str, Enum):
    admin = "Admin"
    member = "Member"


class TaskStatus(str, Enum):
    todo = "To Do"
    in_progress = "In Progress"
    review = "Review"
    done = "Done"


class Priority(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"
    urgent = "Urgent"


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: Role
    created_at: datetime


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ProjectCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=5, max_length=500)
    member_ids: list[str] = []


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, min_length=5, max_length=500)
    member_ids: Optional[list[str]] = None


class ProjectOut(BaseModel):
    id: str
    name: str
    description: str
    owner_id: str
    members: list[str]
    created_at: datetime
    task_count: int = 0
    completed_count: int = 0


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=5, max_length=800)
    project_id: str
    assignee_id: str
    priority: Priority = Priority.medium
    due_date: date

    @field_validator("due_date")
    @classmethod
    def due_date_must_be_valid(cls, value: date) -> date:
        if value.year < 2020:
            raise ValueError("Due date is invalid")
        return value


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=120)
    description: Optional[str] = Field(default=None, min_length=5, max_length=800)
    assignee_id: Optional[str] = None
    priority: Optional[Priority] = None
    due_date: Optional[date] = None
    status: Optional[TaskStatus] = None


class TaskOut(BaseModel):
    id: str
    title: str
    description: str
    project_id: str
    project_name: Optional[str] = None
    assignee_id: str
    assignee_name: Optional[str] = None
    creator_id: str
    status: TaskStatus
    priority: Priority
    due_date: date
    created_at: datetime
    updated_at: datetime
    overdue: bool = False


class DashboardOut(BaseModel):
    total_projects: int
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    by_status: dict[str, int]
    upcoming_tasks: list[TaskOut]
    model_config = ConfigDict(use_enum_values=True)
