from typing import List

from starlette.config import Config
from starlette.datastructures import Secret, CommaSeparatedStrings

API_PREFIX = "/api"

VERSION = "0.0.0.0"

config = Config(".env")

DEBUG: bool = config("DEBUG", cast=bool, default=False)

SECRET_KEY = config("SECRET_KEY", cast=str, default=Secret)

JWT_ALGORITHM = config("ALGORITHM", cast=str, default="HS256")

JWT_ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=30)

PROJECT_NAME: str = config("PROJECT_NAME", default="Card game application")

ALLOWED_HOSTS: List[str] = config(
    "ALLOWED_HOSTS",
    cast=CommaSeparatedStrings,
    default="",
)

GO_SERVER_URL: str = config("GO_SERVER_URL", cast=str, default="http://localhost:8080")

DATABASE_URL: str = config("DB_CONNECTION", cast=str, default='postgresql://')

BOARD_ROW: int = config("BOARD_ROW", cast=int, default=3)
BOARD_COL: int = config("BOARD_COL", cast=int, default=4)

REDIS_URL: str = config("REDIS_URL", cast=str, default='redis://@localhost:6379')

APM_SERVER_URL: str = config("APM_SERVER_URL", cast=str, default="http://localhost:8200")


RABBIT_URL: str = config("RABBIT_URL", cast=str, default="localhost")
RABBIT_PORT: int = config("RABBIT_PORT", cast=int, default=5673)