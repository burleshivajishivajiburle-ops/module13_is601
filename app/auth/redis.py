"""Redis helpers for JWT blacklist management."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Optional, Union

from app.core.config import get_settings

try:  # pragma: no cover - import guard is hard to unit test directly
    import aioredis  # type: ignore
except ModuleNotFoundError as exc:  # Missing distutils on Python 3.12 makes this fail
    aioredis = None  # type: ignore
    _redis_import_error: Optional[Exception] = exc
else:
    _redis_import_error = None

settings = get_settings()

# In-memory fallback storage used when aioredis (or its deps) is unavailable.
_memory_blacklist: Dict[str, int] = {}


async def get_redis():
    """Return a cached Redis connection, if redis support is available."""
    if aioredis is None:
        raise RuntimeError(
            "Redis support is unavailable. Missing dependency:"
            f" {_redis_import_error!r}"
        )

    if not hasattr(get_redis, "redis"):
        get_redis.redis = await aioredis.from_url(
            settings.REDIS_URL or "redis://localhost"
        )
    return get_redis.redis


async def add_to_blacklist(jti: str, exp: Union[int, datetime]) -> None:
    """Add a token's JTI to the blacklist."""
    if isinstance(exp, datetime):
        exp = int(exp.replace(tzinfo=timezone.utc).timestamp())

    if aioredis is None:
        _memory_blacklist[jti] = exp
        return

    redis = await get_redis()
    await redis.set(f"blacklist:{jti}", "1", ex=exp)


async def is_blacklisted(jti: str) -> bool:
    """Check if a token's JTI is blacklisted."""
    if aioredis is None:
        exp = _memory_blacklist.get(jti)
        if exp is None:
            return False

        now = int(datetime.now(timezone.utc).timestamp())
        if exp <= now:
            _memory_blacklist.pop(jti, None)
            return False
        return True

    redis = await get_redis()
    return bool(await redis.exists(f"blacklist:{jti}"))