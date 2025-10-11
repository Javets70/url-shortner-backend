from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import create_db_and_tables
from app.utils import get_rate_limit_key
from app.redis_client import redis_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="URL Shrotner App", debug=True, lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True)


# @app.on_event("startup")
# def startup_event():
#     create_db_and_tables()
#


@app.get("/")
async def root():
    return {"message": "URL Shortner App", "docs": "/docs"}


@app.middleware("http")
async def rate_limiter_middleware(request: Request, call_next):
    rate_limit_key = get_rate_limit_key(request)
    request_per_minute = settings.rate_limit_per_minute
    current_count = redis_service.get_rate_limit(rate_limit_key)

    if current_count >= request_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
        )

    # increment and set rate limit
    redis_service.set_rate_limit(rate_limit_key, 60)

    response = await call_next(request)
    return response


from app.routers.auth import auth_router
from app.routers.urls import urls_router

app.include_router(auth_router)
app.include_router(urls_router)
