from fastapi import Depends, HTTPException
from starlette import status

from card_game.api.dependency.usecase import get_auth_usecase
from card_game.schemas import user as schemas
from card_game.usecase.auth_usecase import oauth2_scheme, AuthenticationUsecase


# get current user by database
async def get_current_user(token: str = Depends(oauth2_scheme),
                           uc: AuthenticationUsecase = Depends(get_auth_usecase)) -> schemas.User:
    try:
        user = uc.token_parse(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.args,
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
