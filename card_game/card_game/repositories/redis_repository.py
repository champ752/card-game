from typing import Optional

import redis

from card_game.constant.constant import REDIS_BOARD_PREFIX_KEY, REDIS_TOKEN_PREFIX_KEY, REDIS_BOARD_CONFIG_KEY, \
    REDIS_GLOBAL_BEST_KEY
from card_game.schemas.board import RedisBoard, BoardConfig
from card_game.schemas.user import UserInRedis, GlobalBest


class BaseRedisRepository:
    def __init__(self, conn: redis.Redis) -> None:
        self._conn = conn


class RedisRepository(BaseRedisRepository):
    def __init__(self, conn: redis.Redis):
        super().__init__(conn)

    def set_board(self, user_id: str, board: RedisBoard) -> None:
        print(board.id)
        # marshal result to json
        b = board.json()
        print(b)
        self._conn.set(REDIS_BOARD_PREFIX_KEY + user_id, b)

    def get_board(self, user_id: str) -> RedisBoard or None:
        data = self._conn.get(REDIS_BOARD_PREFIX_KEY + str(user_id))
        print(data)
        if data is None:
            return None
        # unmarshal result to object
        return RedisBoard.parse_raw(data)

    def delete_board(self, user_id: str):
        self._conn.delete(REDIS_BOARD_PREFIX_KEY + str(user_id))

    def set_user(self, usr: UserInRedis):
        b = usr.json()
        self._conn.set(REDIS_TOKEN_PREFIX_KEY + str(usr.id), b)

    def get_user(self, user_id) -> UserInRedis or None:
        data = self._conn.get(REDIS_TOKEN_PREFIX_KEY + str(user_id))
        if data is None:
            return None
        return UserInRedis.parse_raw(data)

    # set board dimension config
    def set_board_config(self, board_config: BoardConfig) -> None:
        b_cfg = board_config.json()
        self._conn.set(REDIS_BOARD_CONFIG_KEY, b_cfg)

    def get_board_config(self) -> BoardConfig or None:
        data = self._conn.get(REDIS_BOARD_CONFIG_KEY)
        if data is None:
            return None
        return BoardConfig.parse_raw(data)

    # delete all cache board
    def delete_all_board(self) -> None:
        for key in self._conn.scan_iter(REDIS_BOARD_PREFIX_KEY + "*"):
            self._conn.delete(key)

    def get_global_best(self) -> GlobalBest or None:
        data = self._conn.get(REDIS_GLOBAL_BEST_KEY)
        if data is None:
            return None
        return GlobalBest.parse_raw(data)

    def set_global_best(self, global_best: GlobalBest) -> None:
        best = global_best.json()
        self._conn.set(REDIS_GLOBAL_BEST_KEY, best)
