from fastapi import Depends
from redis import Redis
from sqlalchemy.orm import Session

from card_game.api.dependency.database import redis_connection, get_db
from card_game.repositories.redis_repository import RedisRepository
from card_game.repositories.user_repository import UserRepository
from card_game.usecase.auth_usecase import AuthenticationUsecase
from card_game.usecase.game_usecase import GameUsecase
from card_game.usecase.user_usecase import UserUsecase


def get_game_usecase(r: Redis = Depends(redis_connection), conn: Session = Depends(get_db)) -> GameUsecase:
    redis_repo: RedisRepository = RedisRepository(r)
    user_repo: UserRepository = UserRepository(conn)
    return GameUsecase(redis_repo, user_repo)


def get_user_usecase(conn: Session = Depends(get_db)) -> UserUsecase:
    user_repo: UserRepository = UserRepository(conn)
    return UserUsecase(user_repo)


def get_auth_usecase(conn: Session = Depends(get_db), r: Redis = Depends(redis_connection)) -> AuthenticationUsecase:
    user_repo: UserRepository = UserRepository(conn)
    redis_repo: RedisRepository = RedisRepository(r)
    return AuthenticationUsecase(user_repo, redis_repo)
