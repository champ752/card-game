from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from card_game.api.dependency.usecase import get_auth_usecase
from card_game.schemas.token import Token
from card_game.usecase.auth_usecase import AuthenticationUsecase

router = APIRouter()


@router.post("/token", response_model=Token, tags=["auth"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), uc: AuthenticationUsecase = Depends(get_auth_usecase)):
    try:
        return uc.login(form_data.username, form_data.password)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.args,
            headers={"WWW-Authenticate": "Bearer"},
        )
