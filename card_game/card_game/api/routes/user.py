from fastapi import APIRouter, Depends, HTTPException

from card_game.api.dependency.authentication import get_current_user
from card_game.api.dependency.usecase import get_user_usecase
from card_game.usecase.user_usecase import UserUsecase
from card_game.schemas import user as schemas
from card_game.entities import user as entities

router = APIRouter()


@router.post("/", response_model=schemas.User, tags=["user"])
def create_new_user(req: schemas.UserCreate, uc: UserUsecase = Depends(get_user_usecase)):
    try:
        res: entities.User = uc.create_user(req)
    except Exception as e:
        raise HTTPException(status_code=422, detail=e.args)

    return schemas.User(id=res.id, username=res.username, best=res.best)


@router.get("/", response_model=schemas.User, tags=["user"])
def get_current_login_in_user_info(session_user: schemas.User = Depends(get_current_user)):
    return session_user
