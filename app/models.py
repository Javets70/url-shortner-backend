from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timedelta
from enum import Enum
from pydantic import EmailStr


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    email: EmailStr = Field(unique=True)
    hashed_password: str
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now(datetime.timezone.utc))

    # Relationships
    urls: List["ShortURL"] = Relationship(back_populates="owner")


class ShortURL(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    short_code: str = Field(unique=True)
    original_url: str

    title: Optional[str] = None
    description: Optional[str] = None

    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now(datetime.timezone.utc))
    expires_at: Optional[datetime] = Field(default=None)
    visit_count: int = Field(default=0)
    last_visited: Optional[datetime] = Field(default=None)

    owner_id: int = Field(foreign_key="user.id")

    # Relationships
    owner: User = Relationship(back_populates="urls")


# class Token(BaseModel):
#     access_token: str
#     token_type: str


# class TokenData(BaseModel):
#     username: str | None = None
