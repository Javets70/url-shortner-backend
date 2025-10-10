import string
import random
from sqlmodel import Session, select
from datetime import datetime, timezone, timedelta
from typing import Optional

from app.config import settings
from app.models import ShortURL, URLCreate, URLAnalytics
from app.redis_client import redis_service
from app.utils import get_url_cache_key


class URLService:
    def __init__(self):
        self.base_url = settings.base_url

    def generate_short_code(self, length: int = 6):
        characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for _ in range(length))

    def create_short_url(
        self, session: Session, url_data: URLCreate, user_id: int
    ) -> ShortURL:
        while True:
            short_code = self.generate_short_code()
            existing = session.exec(
                select(ShortURL).where(ShortURL.short_code == short_code)
            ).first()
            if not existing:
                break

        expires_at = datetime.now(timezone.utc) + timedelta(
            url_data.expires_in_days or settings.url_default_expiry_days
        )

        short_url = ShortURL(
            short_code=short_code,
            original_url=url_data.original_url,
            title=url_data.title,
            description=url_data.description,
            expires_at=expires_at,
            owner_id=user_id,
        )

        session.add(short_url)
        session.commit()
        session.refresh(short_url)

        redis_service.publish_message(
            "url_created",
            {
                "url_id": short_url.id,
                "short_code": short_code,
                "original_url": url_data.original_url,
                "user_id": user_id,
                "created_at": short_url.created_at.isoformat(),
            },
        )

        return short_url

    def get_url_by_code(self, session: Session, short_code: str) -> Optional[ShortURL]:
        cache_key = get_url_cache_key(short_code)
        cached_url = redis_service.get_cache(cache_key)

        if cached_url:
            return ShortURL(**cached_url)

        statement = select(ShortURL).where(
            ShortURL.short_code == short_code, ShortURL.is_active == True
        )
        url = session.exec(statement).first()

        if url:
            url_dict = {
                "id": url.id,
                "short_code": url.short_code,
                "original_url": url.original_url,
                "title": url.title,
                "description": url.description,
                "is_active": url.is_active,
                "created_at": url.created_at.isoformat(),
                "expires_at": url.expires_at.isoformat() if url.expires_at else None,
                "visit_count": url.visit_count,
                "last_visited": (
                    url.last_visited.isoformat() if url.last_visited else None
                ),
                "owner_id": url.owner_id,
            }
            redis_service.set_cache(
                cache_key, url_dict, expire=settings.default_cache_expiry_seconds
            )

        return url

    def increment_visit_count(
        self,
        session: Session,
        url: ShortURL,
        ip_address: str,
        user_agent: str = None,
        referer: str = None,
    ) -> ShortURL:
        """Increment visit count and publish redis events for expiry and visit threshold"""
        url.visit_count += 1
        url.last_visited = datetime.now(timezone.utc)
        session.add(url)
        session.commit()

        analytics = URLAnalytics(
            url_id=url.id, ip_address=ip_address, user_agent=user_agent, referer=referer
        )
        session.add(analytics)
        session.commit()

        if url.visit_count == settings.visit_threshold:
            redis_service.publish_message(
                "visit_threshold_reached",
                {
                    "url_id": url.id,
                    "short_code": url.short_code,
                    "visit_count": url.visit_count,
                    "user_id": url.owner_id,
                },
            )

        if url.expires_at:
            days_until_expiry = (url.expires_at - datetime.now(timezone.utc)).days
            if days_until_expiry <= settings.expiration_warning_days:
                redis_service.publish_message(
                    "url_expiring_soon",
                    {
                        "url_id": url.id,
                        "short_code": url.short_code,
                        "expires_at": url.expires_at.isoformat(),
                        "days_until_expiry": days_until_expiry,
                        "user_id": url.owner_id,
                    },
                )

        return url


url_service = URLService()
