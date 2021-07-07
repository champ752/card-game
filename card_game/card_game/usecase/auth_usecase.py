import uuid
from datetime import timedelta, datetime
from typing import Optional

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError

from card_game.configs.config import SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES
from card_game.constant.constant import JWT_TOKEN_PREFIX
from card_game.repositories.redis_repository import RedisRepository
from card_game.repositories.user_repository import UserRepository
from card_game.schemas.token import TokenData
from card_game.schemas.user import UserInRedis
from card_game.schemas import user as schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


class AuthenticationUsecase:
    def __init__(self, user_repo: UserRepository, redis_repo: RedisRepository):
        self._user_repo = user_repo
        self._redis_repo = redis_repo

    def _verify_password(self, plain_password: str, hashed_password: str):
        return pwd_context.verify(plain_password, hashed_password)

    def _get_password_hash(self, password) -> str:
        return pwd_context.hash(password)

    def authenticate_user(self, username: str, password: str):
        user = self._user_repo.get_user_by_username(username)
        if not user:
            return False
        if not self._verify_password(password, user.password):
            return False
        return user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt

    def login(self, username: str, password: str):
        user = self.authenticate_user(username, password)
        if not user:
            raise Exception("Incorrect username or password")

        access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )

        self._redis_repo.set_user(UserInRedis(best=user.best, token=access_token, username=user.username, id=user.id))

        return {"access_token": access_token, "token_type": JWT_TOKEN_PREFIX}

    def token_parse(self, token):
        credentials_exception = Exception("Could not validate credentials")
        token_expire = Exception("Token expired please re-login")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                raise credentials_exception

            redis_user = self._redis_repo.get_user(user_id)
            # Check token redis
            if redis_user is not None:
                # Check current token session if not current return 401 status
                if redis_user.token != token:
                    raise token_expire
                # Return user detail from redis
                return schemas.User(id=redis_user.id, username=redis_user.username, best=redis_user.best)
        except JWTError:
            raise credentials_exception

        db_user = self._user_repo.get_user(uuid.UUID(user_id))
        if db_user is None:
            raise credentials_exception

        return schemas.User(id=db_user.id, username=db_user.username, best=db_user.best)