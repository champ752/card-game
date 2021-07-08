import uuid
from typing import List

from pydantic import BaseModel

from card_game.schemas.card import Card, ResumeCard


class RedisBoard(BaseModel):
    board: List[Card]
    click: int
    id: uuid.UUID


class BoardConfig(BaseModel):
    board_row: int
    board_col: int


class ResumeBoard(BaseModel):
    click: int
    board: List[ResumeCard]

class InitBoardResponse(BaseModel):
    status: bool