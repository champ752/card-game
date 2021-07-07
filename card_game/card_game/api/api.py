from fastapi import APIRouter

from card_game.api.routes import board, card, user, auth

api_router = APIRouter()

# api route
api_router.include_router(router=board.router, prefix="/board")
api_router.include_router(router=card.router, prefix="/card")
api_router.include_router(router=user.router, prefix="/user")
api_router.include_router(router=auth.router, prefix="/auth")
