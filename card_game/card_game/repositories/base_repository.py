import redis
from sqlalchemy.orm import Session
from .database import Base
from ..entities.user import User


class BaseRepository:
    def __init__(self, conn: Session) -> None:
        self._conn = conn

