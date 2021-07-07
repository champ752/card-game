import math
import uuid
from typing import List, Type, Optional

from card_game.configs.config import BOARD_ROW, BOARD_COL
from card_game.constant.constant import ERROR_NOT_FOUND_BOARD, ERROR_GAME_NOT_INITIALIZE, ERROR_CARD_ALREADY_OPEN, \
    ERROR_BOARD_SIZE_INVALID
from card_game.schemas.board import RedisBoard, ResumeBoard
from card_game.schemas.card import Card, OpenCardRequest, OpenCardResponse, ResumeCard
import numpy as np

from card_game.schemas.user import GlobalBest, User


class GameUsecase:
    def __init__(
            self,
            redis_repo, user_repo=None,
            board: Optional[List[Card]] = None,
            click: Optional[int] = 0,
            board_uuid: Optional[uuid.UUID] = None
    ):

        self._redis_repo = redis_repo
        self._user_repo = user_repo

        if board is not None:
            self.board: List[Card] = board
        else:
            self.board: List[Card] = []

        self.click: int = click
        self.id = board_uuid

    def _convert_matrix_index_to_array_index(self, row, col) -> int:
        return (row * BOARD_COL) + col

    def _convert_array_index_to_matrix_index(self, idx) -> (int, int):
        row = math.floor(idx / BOARD_COL)
        col = idx % BOARD_COL
        return row, col

    def _find_unmatched_card(self) -> int:
        for card_idx in range(0, len(self.board)):
            if self.board[card_idx].is_open and not self.board[card_idx].is_match:
                return card_idx
        return -1

    def all_match(self) -> bool:
        for card_idx in range(0, len(self.board)):
            if not self.board[card_idx].is_match:
                return False
        return True

    def open_card(self, req: OpenCardRequest) -> OpenCardResponse:
        response: OpenCardResponse

        if len(self.board) == 0:
            raise Exception(ERROR_GAME_NOT_INITIALIZE)

        # convert 2d to 1d array index such as [1][3] -> 7
        card_idx = self._convert_matrix_index_to_array_index(req.row, req.col)

        # open the card that already opened.
        if self.board[card_idx].is_open:
            raise Exception(ERROR_CARD_ALREADY_OPEN)

        # card that already opened without pair
        opened_card_idx = self._find_unmatched_card()
        # add action
        self.click += 1

        # card unmatched is not open
        if opened_card_idx == -1 and not self.all_match():
            self.board[card_idx].is_open = True
            card: Card = self.board[card_idx]

            # open new card
            response = OpenCardResponse(number=card.number, is_open=True)

        else:
            # card unmatched open and same number as opening card
            if self.board[card_idx].number == self.board[opened_card_idx].number:

                # open incoming card
                self.board[card_idx].is_open = True
                self.board[card_idx].is_match = True

                # match opened card
                self.board[opened_card_idx].is_match = True

                card: Card = self.board[card_idx]

                # open new card and match with previous card
                response = OpenCardResponse(number=card.number, is_open=True, is_match=True)
            else:
                self.board[opened_card_idx].is_open = False

                # open new card and flip previous card and this card down
                card: Card = self.board[card_idx]

                response = OpenCardResponse(number=card.number, is_open=False, is_match=False)

        if self.all_match():
            # delete finish board from redis
            self._redis_repo.delete_board(user_id=str(req.user_id))

            # update best to user
            self._user_repo.update_best(req.user_id, self.click)

            current_best = self.get_global_best()
            if self.click < current_best.global_best:
                self.update_global_best(GlobalBest(global_best=self.click))
            # win match
            response = OpenCardResponse(number=card.number, is_open=True, is_match=True, is_win=True)
        else:
            self._redis_repo.set_board(str(req.user_id), RedisBoard(board=self.board, click=self.click, id=self.id))
        self.print_board()
        return response

    def print_board(self):
        reshaped_lst = np.reshape(self.board, (BOARD_ROW, BOARD_COL))
        for i in range(0, len(reshaped_lst)):
            for j in range(0, len(reshaped_lst[i])):
                print(reshaped_lst[i][j].number, " is open", reshaped_lst[i][j].is_open, end=",")
            print()

    def create_board(self, user: User) -> List[Card]:
        if (BOARD_ROW * BOARD_COL) % 2 != 0:
            raise Exception(ERROR_BOARD_SIZE_INVALID)

        # find card max number 4*3 = 12 will be 6
        max_number: int = int((BOARD_ROW * BOARD_COL) / 2)

        # generate [0,...5] + 1 -> [1,...6]
        number_lst = np.arange(max_number) + 1

        # repeat it 2 times make a pair
        random_value_lst = [*number_lst, *number_lst]

        # shuffle position of cards
        np.random.shuffle(random_value_lst)
        board: List[Card] = []

        for i in range(0, len(random_value_lst)):
            board.append(Card(number=random_value_lst[i]))

        self._redis_repo.set_board(str(user.id), RedisBoard(board=board, click=0, id=str(uuid.uuid4())))

        # TODO send to log

        return board

    def get_board(self, username) -> RedisBoard:
        r_board = self._redis_repo.get_board(username)
        if r_board is None:
            raise Exception(ERROR_NOT_FOUND_BOARD)
        return r_board

    def set_board_by_user_id(self, user_id):
        r_board: RedisBoard = self._redis_repo.get_board(str(user_id))
        if r_board is not None:
            self.board = r_board.board
            self.click = r_board.click
            self.id = r_board.id

    def resume_board(self, user: User) -> ResumeBoard:
        r_board = self._redis_repo.get_board(user.id)
        if r_board is None:
            raise Exception(ERROR_NOT_FOUND_BOARD)
        board: List[ResumeCard] = []
        for i in range(0, len(r_board.board)):
            row, col = self._convert_array_index_to_matrix_index(i)
            if r_board.board[i].is_open or r_board.board[i].is_match:
                board.append(
                    ResumeCard(row=row, col=col, number=r_board.board[i].number, is_match=r_board.board[i].is_match))
        return ResumeBoard(board=board, click=r_board.click)

    def update_global_best(self, best: GlobalBest):
        self._redis_repo.set_global_best(best)

    def get_global_best(self) -> GlobalBest:
        best: GlobalBest = self._redis_repo.get_global_best()
        # Not in cache
        if best is None:
            db_global_best = self._user_repo.get_global_best()
            best = GlobalBest(global_best=db_global_best)
            self._redis_repo.set_global_best(best)
            return best
        return best
