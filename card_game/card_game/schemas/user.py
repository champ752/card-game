import uuid

from pydantic import BaseModel

from card_game.schemas.base import EntitySchema


class UserByIdRequest(BaseModel):
    id: uuid.UUID


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str
    class Config:
        schema_extra = {
            "example": {
                "username": "user",
                "password": "password"
            }
        }


class User(EntitySchema, UserBase):
    id: uuid.UUID
    best: int


class UserInRedis(User):
    token: str


class GlobalBest(BaseModel):
    global_best: int
