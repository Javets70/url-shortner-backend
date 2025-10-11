from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.models import URLCreate, User
from app.auth import get_current_active_user
from app.database import get_session
from app.url_service import url_service

urls_router = APIRouter(prefix="/urls", tags=["urls"])


@urls_router.post("/")
def create_short_url(
    url_data: URLCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
):
    try:
        short_url = url_service.create_short_url(session, url_data, current_user.id)
        return URLResponse(
            id=short_url.id,
            short_code=short_url.short_code,
            short_url=f"{url_service.base_url}/{short_url.short_code}",
            original_url=short_url.original_url,
            title=short_url.title,
            description=short_url.description,
            is_active=short_url.is_active,
            created_at=short_url.created_at,
            expires_at=short_url.expires_at,
            visit_count=short_url.visit_count,
            last_visited=short_url.last_visited,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create short URL: {str(e)}",
        )


# @urls_router.get("/")
# async def get_user_urls(
#     skip: int = 0,
#     limit: int = 100,
#     current_user: User = Depends(get_current_active_user),
#     session: Session = Depends(get_session),
# ):
#     urls = url_service.get_user_urls(session, current_user.id, skip, limit)


@urls_router.delete(f"/{url_id}/")
async def deactivate_url(
    url_id: int,
    current_user: User = Depends(get_session),
    session: Session = Depends(get_session),
):
    success = url_service.deactivate_url(session, url_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
        )

    return {"message": "URL deactivated successfully"}


@router.get("/redirect/{short_code}")
async def redirect_url(
    short_code: str, request: Request, session: Session = Depends(get_session)
):

    url = url_service.get_url_by_code(session, short_code)

    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found"
        )

    if url.expires_at and url.expires_at < url.created_at.replace(tzinfo=None):
        raise HTTPException(
            status_code=status.HTTP_410_GONE, detail="Short URL has expired"
        )

    client_ip = request.client.host
    user_agent = request.headers.get("user-agent")
    referer = request.headers.get("referer")

    url_service.increment_visit_count(
        session, url, ip_address=client_ip, user_agent=user_agent, referer=referer
    )

    return RedirectResponse(url=url.original_url, status_code=302)
