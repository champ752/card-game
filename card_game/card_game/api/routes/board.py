from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from card_game.api.dependency.authentication import get_current_user
from card_game.schemas.board import ResumeBoard
from card_game.schemas.user import GlobalBest, User
from card_game.api.dependency.usecase import get_game_usecase, get_user_usecase
from card_game.usecase.game_usecase import GameUsecase

router = APIRouter()


@router.get("/start", tags=['board'], status_code=201)
def init_board(uc: GameUsecase = Depends(get_game_usecase), current_user: User = Depends(get_current_user)):
    """
      Create an board for all the information
      \f
      :param uc: GameUsecase contain business logic for game.
      :param current_user: Session user for assign created game to user and store to redis.
      """
    uc.create_board(current_user)
    return {"success": True}


@router.get("/global/best", response_model=GlobalBest, tags=["board"])
def get_global_best(uc: GameUsecase = Depends(get_game_usecase)):
    """
      Get an global best for all user in system
      \f
      :param uc: UserUsecase contain business logic for user.
      """
    return uc.get_global_best()


@router.get("/", tags=['board'], response_model=ResumeBoard)
def get_playing_board(uc: GameUsecase = Depends(get_game_usecase), current_user: User = Depends(get_current_user)):
    """
       Get an board that user playing in last session
       \f
       :param uc: UserUsecase contain business logic for user.
       :param current_user: Session user for assign get current game session.
       """
    try:
        return uc.resume_board(current_user)
    except Exception as e:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=e.args)
