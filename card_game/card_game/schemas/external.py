import uuid
from typing import List

from pydantic import BaseModel


class Action(BaseModel):
    number: int
    arr_idx: int


class BoardAndAction(BaseModel):
    status: bool
    board_id: uuid.UUID
    user_id: uuid.UUID
    board_data: str
    actions: List[Action]


class CreateBoardLog(BaseModel):
    board_id: uuid.UUID
    user_id: uuid.UUID
    board_data: str


class CreateActionLog(Action):
    board_id: uuid.UUID
