from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from card_game.api.dependency.database import redis_connection
from card_game.configs.config import PROJECT_NAME, DEBUG, VERSION, ALLOWED_HOSTS, API_PREFIX, APM_SERVER_URL, BOARD_COL, \
    BOARD_ROW
from card_game.api import api
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM
from card_game.repositories.redis_repository import RedisRepository
from card_game.schemas.board import BoardConfig
from fastapi.exceptions import RequestValidationError

tags_metadata = [
    {
        "name": "board",
        "description": "Operation with card board. Functions in this routes are getting new game, global best score and resume game"
    },
    {
        "name": "card",
        "description": "Operation with card flip on to the board. Condition about open card, match card and win"
    },
    {
        "name": "user",
        "description": "Operation with user. Functions in this routes are create and get user info"
    },
    {
        "name": "auth",
        "description": "authentication route for user"
    }
]


def check_config():
    # check board size should be even number for generate pair of value
    if (BOARD_COL * BOARD_ROW) % 2 != 0:
        raise Exception("board size should be even number")
    r: RedisRepository = RedisRepository(redis_connection())
    b_cfg: BoardConfig = r.get_board_config()

    # not config in redis add it
    if b_cfg is None:
        r.set_board_config(BoardConfig(board_row=BOARD_ROW, board_col=BOARD_COL))
    else:
        # new config is being set
        if b_cfg.board_col != BOARD_COL or b_cfg.board_row != BOARD_ROW:
            # delete all current board
            r.delete_all_board()
            # update board config
            r.set_board_config(BoardConfig(board_row=BOARD_ROW, board_col=BOARD_COL))


def get_application() -> FastAPI:
    apm = make_apm_client({'SERVICE_NAME': 'card_game', 'SERVER_URL': APM_SERVER_URL})
    application = FastAPI(title=PROJECT_NAME, debug=DEBUG, version=VERSION, openapi_tags=tags_metadata)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_HOSTS or ["*"],
        allow_methods=["*"],
        allow_headers=["*"]
    )

    check_config()

    application.add_middleware(ElasticAPM, client=apm)
    application.include_router(prefix=API_PREFIX, router=api.api_router)
    return application


app = get_application()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse({"detail": ["something went wrong"]}, status_code=422)
