"""Redis client for caching and session management."""
import json
from typing import Optional, Any
import redis

from app.core.config import settings

# Redis connection
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def cache_set(
    key: str,
    value: Any,
    expire: int = 3600
) -> None:
    """Set value in cache with optional expiry (seconds)."""
    try:
        redis_client.setex(
            key,
            expire,
            json.dumps(value) if not isinstance(value, str) else value
        )
    except redis.RedisError as e:
        print(f"Redis error setting key {key}: {e}")


def cache_get(key: str) -> Optional[Any]:
    """Get value from cache."""
    try:
        value = redis_client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    except redis.RedisError as e:
        print(f"Redis error getting key {key}: {e}")
        return None


def cache_delete(key: str) -> None:
    """Delete key from cache."""
    try:
        redis_client.delete(key)
    except redis.RedisError as e:
        print(f"Redis error deleting key {key}: {e}")


def cache_exists(key: str) -> bool:
    """Check if key exists in cache."""
    try:
        return redis_client.exists(key) > 0
    except redis.RedisError as e:
        print(f"Redis error checking key {key}: {e}")
        return False
