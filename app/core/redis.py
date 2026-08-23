"""Redis client for token blacklisting."""
import redis
from app.config import get_settings

settings = get_settings()

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def blacklist_token(token: str, expires_in: int) -> None:
    """Add a token to the blacklist. """
    redis_client.setex(f"blacklist:{token}", expires_in, "1")

def is_token_blacklisted(token: str) -> bool:
    """Check if a token is blacklisted."""
    return redis_client.exists(f"blacklist:{token}") > 0

