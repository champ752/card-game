from fastapi import APIRouter, Depends, Path, HTTPException

from card_game.api.dependency.authentication import get_current_user
from card_game.api.dependency.usecase import get_game_usecase
from card_game.configs.config import BOARD_ROW, BOARD_COL
from card_game.schemas.card import OpenCardRequest, OpenCardResponse
from card_game.schemas.user import User
from card_game.usecase.game_usecase import GameUsecase

router = APIRouter()


@router.get("/open/{board_row}/{board_col}", response_model=OpenCardResponse, tags=['card'])
def open_a_card(board_row: int = Path(..., ge=0, lt=BOARD_ROW,description="row of the board index (2d array index) start with 0 not more than " + str(BOARD_ROW-1)),
                board_col: int = Path(..., ge=0, lt=BOARD_COL,description="col of the board index (2d array index) start with 0 not more than " + str(BOARD_COL-1)),
                uc: GameUsecase = Depends(get_game_usecase), current_user: User = Depends(get_current_user)):
    """
        Open card from current board example [[1,2,3,4],[5,6,7,8],[9,10,11,12]] row = 3, column = 4 -> [row][column]
          - **board_row**: board row index start with 0
          - **board_col**: board column index start with 0
         - Open a card match with previous opened card.  Flag is_match and is_open will be true
         - Open a card not match and not have non match card open. Flag is_open will be true
         - Open a card not match and have non match card open. Flag is_open will be false
         - Open the last card and wining the game. Flag is_win will be true

        \f
        :param board_row: board row index in 2d array board index start from 0
        :param board_col: board column index in 2d array board index start from 0
        :param uc: GameUsecase contain business logic for game.
        :param current_user: Session user for assign get current game session.
        """
    req = OpenCardRequest(row=board_row, col=board_col, user_id=current_user.id)

    try:
        uc.set_board_by_user_id(current_user.id)
        return uc.open_card(req)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e.args)
