from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timezone
from enum import Enum
from pydantic import EmailStr


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    email: EmailStr = Field(unique=True)
    hashed_password: str
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))

    # Relationships
    urls: List["ShortURL"] = Relationship(back_populates="owner")
    analytics: List["URLAnalytics"] = Relationship(back_populates="user")


class ShortURL(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    short_code: str = Field(unique=True)
    original_url: str

    title: Optional[str] = None
    description: Optional[str] = None

    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    expires_at: Optional[datetime] = Field(default=None)
    visit_count: int = Field(default=0)
    last_visited: Optional[datetime] = Field(default=None)

    owner_id: int = Field(foreign_key="user.id")

    # Relationships
    owner: User = Relationship(back_populates="urls")
    analytics: List["URLAnalytics"] = Relationship(back_populates="url")


class URLAnalytics(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referer: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    visited_at: datetime = Field(default_factory=datetime.now(timezone.utc))

    url_id: int = Field(foreign_key="shorturl.id")
    user_id: int = Field(foreign_key="user.id")

    # Relationships
    user: User = Relationship(back_populates="analytics")
    url: ShortURL = Relationship(back_populates="analytics")


class UserCreate(SQLModel):
    username: str
    email: str
    password: str


class UserLogin(SQLModel):
    username: str
    password: str


class UserResponse(SQLModel):
    id: int
    username: str
    # email:str
    role: UserRole
    is_active: bool
    created_at: datetime


class Token(SQLModel):
    access_token: str
    token_type: str


class URLCreate(SQLModel):
    original_url: str
    title: Optional[str] = None
    description: Optional[str] = None
    expires_in_days: Optional[int] = None


class URLResponse(SQLModel):
    id: int
    short_code: str
    short_url: str
    original_url: str
    title: Optional[str]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime]
    visit_count: int
    last_visited: Optional[datetime]


class URLAnalyticsResponse(SQLModel):
    total_visits: int
    unique_visitors: int
    visits_by_country: dict
    visits_by_date: dict
    top_referers: List[dict]


# class TokenData(BaseModel):
#     username: str | None = None
