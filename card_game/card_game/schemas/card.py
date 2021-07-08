import uuid
from typing import Optional

from pydantic import BaseModel


class Card(BaseModel):
    number: int
    is_open: Optional[bool] = False
    is_match: Optional[bool] = False


class OpenCardRequest(BaseModel):
    row: int
    col: int
    user_id: uuid.UUID


class OpenCardResponse(BaseModel):
    number: int
    is_open: Optional[bool] = False
    is_match: Optional[bool] = False
    is_win: Optional[bool] = False


class ResumeCard(BaseModel):
    row: int
    col: int
    number: int
    is_match: Optional[bool] = False
