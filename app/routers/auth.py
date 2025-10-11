from fastapi import APIRouter, status, HTTPException, Depends
from sqlmodel import Session, select

from app.models import User, UserResponse, UserCreate, Token, UserLogin
from app.database import get_session
from app.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    refresh_access_token,
)

auth_router = APIRouter(prefix="/auth", tags=["authentication"])


@auth_router.post("/register/", response_model=UserResponse)
async def register(user_data: UserCreate, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == user_data.username)
    user = session.exec(statement).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    statement = select(User).where(User.email == user_data.email)
    user = session.exec(statement).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
    )

    session.add(user)
    session.commit()
    session.refresh()

    return UserResponse(
        id=user.id,
        username=user.usernamae,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@auth_router.post("/login/", response_model=Token)
async def login(user_credentials: UserLogin, session: Session = Depends(get_session)):
    user = authenticate_user(
        session, user_credentials.username, user_credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")


@auth_router.post("/refresh-token/", response_model=Token)
async def refresh_token(old_token: str):
    token = Token(access_token=refresh_access_token(old_token), token_type="bearer")
    return token
