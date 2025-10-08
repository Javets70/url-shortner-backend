import redis
from redis import Redis
import json
from typing import Optional, Any

from app.settings import settings

redis_client: Redis = redis.from_url(settings.redis_url, decode_responses=True)


class RedisService:
    def __init__(self):
        self.client = redis_client

    def set_cache(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = settings.default_cache_expiry_seconds,
    ) -> bool:
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return self.client.set(key, value, expire)
        except Exception as e:
            return False

    def get_cache(self, key: str) -> Optional[Any]:
        try:
            value = self.client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            return False

    def delete_cache(self, key: str) -> bool:
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            return False

    def increment_counter(self, key: str, amount: int = 1) -> int:
        try:
            return self.client.incrby(key, amount)
        except Exception as e:
            return 0

    def set_expire(self, key: str, seconds: int) -> bool:
        try:
            return self.client.expire(key, seconds)
        except Exception as e:
            return False

    def publish_message(self, channel: str, message: dict) -> bool:
        try:
            return self.client.publish(channel, json.dumps(message))
        except Exception as e:
            return False

    def get_rate_limit(self, key: str) -> int:
        try:
            count = self.client.get(key)
            return int(count) if count else 0
        except Exception as e:
            return False

    def set_rate_limit(self, key: str, seconds: int) -> bool:
        try:
            pipe = self.client.pipeline()
            pipe.incr(key)
            pipe.expire(key, seconds)
            pipe.execute()
            return True
        except Exception as e:
            return False


redis_service = RedisService()
