from functools import lru_cache

from redis import Redis, StrictRedis

from card_game.configs.config import REDIS_URL
from card_game.repositories.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@lru_cache(maxsize=1)
def redis_connection() -> Redis:
    """Return the Redis connection to the URL given by the environment
    variable REDIS_URL, creating it if necessary.

    """
    return StrictRedis.from_url(REDIS_URL)
