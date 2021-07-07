from functools import lru_cache

import pika
from redis import Redis, StrictRedis

from card_game.configs.config import REDIS_URL, RABBIT_URL, RABBIT_PORT
from card_game.repositories.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def rabbit_connection():
    return pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_URL, port=RABBIT_PORT))


@lru_cache(maxsize=1)
def redis_connection() -> Redis:
    """Return the Redis connection to the URL given by the environment
    variable REDIS_URL, creating it if necessary.

    """
    return StrictRedis.from_url(REDIS_URL)
