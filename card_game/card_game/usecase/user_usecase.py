from passlib.context import CryptContext

from card_game.constant.constant import ERROR_USER_ALREADY_REGISTERED
from card_game.entities import user as entities
from card_game.repositories.user_repository import UserRepository
from card_game.schemas.user import UserCreate, UserByIdRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserUsecase:
    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repository = user_repo

    def find_user_by_id(self, usr: UserByIdRequest) -> entities.User:
        return self._user_repository.get_user(user_id=usr.id)

    def create_user(self, usr: UserCreate) -> entities.User:
        usr_db = self._user_repository.get_user_by_username(username=usr.username)
        if usr_db:
            raise Exception(ERROR_USER_ALREADY_REGISTERED)
        usr.password = self.get_password_hash(usr.password)
        return self._user_repository.create_user(usr)

    def get_password_hash(self, password):
        return pwd_context.hash(password)
