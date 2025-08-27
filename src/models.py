from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


class Signup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_email: str
    activity_id: int = Field(foreign_key="activity.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Activity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    schedule: Optional[str] = None
    max_participants: Optional[int] = None

    signups: List[Signup] = Relationship(back_populates="activity")


Signup.activity = Relationship(back_populates="signups")
