import uuid

from sqlalchemy import func
from sqlalchemy.orm import Session

from card_game.entities import user as entities
from card_game.repositories.base_repository import BaseRepository
from card_game.schemas import user as schemas


class UserRepository(BaseRepository):
    def __init__(self, conn: Session):
        super().__init__(conn)

    def create_user(self, user: schemas.UserCreate) -> entities.User:
        db_user: entities.User = entities.User(username=user.username, password=user.password)
        self._conn.add(db_user)
        self._conn.commit()
        self._conn.refresh(db_user)
        return db_user

    def get_user(self, user_id: uuid.UUID) -> entities.User:
        return self._conn.query(entities.User).filter(entities.User.id == user_id).first()

    def get_user_by_username(self, username: str) -> entities.User:
        return self._conn.query(entities.User).filter(entities.User.username == username).first()

    def update_best(self, user_id: uuid.UUID, best: int):
        self._conn.flush()
        user = self._conn.query(entities.User).filter(entities.User.id == user_id).first()
        if user.best == 0 or user.best > best:
            user.best = best
        self._conn.commit()

    def get_global_best(self) -> int:
        return self._conn.query(func.min(entities.User.best)).scalar()
