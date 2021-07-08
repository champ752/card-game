import unittest
import uuid
from unittest import mock
from unittest.mock import MagicMock, Mock

from card_game import __version__
from card_game.configs.config import BOARD_COL, BOARD_ROW
from card_game.constant.constant import ERROR_NOT_FOUND_BOARD
from card_game.schemas.board import RedisBoard, ResumeBoard
from card_game.schemas.card import Card, OpenCardRequest
from card_game.schemas.external import BoardAndAction, Action
from card_game.schemas.user import User, GlobalBest
from card_game.usecase.game_usecase import GameUsecase


def test_version():
    assert __version__ == '0.1.0'


class TestGameUsecase(unittest.TestCase):
    @mock.patch('card_game.repositories.redis_repository.RedisRepository')
    def setUp(self, mock_repo):
        self.redis_mock_repo = mock_repo
        self.board_id = uuid.uuid4()
        self.user_id = uuid.uuid4()
        self.usecase = GameUsecase(self.redis_mock_repo, user_repo=MagicMock(), log_repo=MagicMock(),
                                   board_uuid=self.board_id)

        self.fix_data = [4, 2, 4, 2, 3, 3, 5, 6,
                         6, 1, 5, 1]
        self.mock_user: User = User(id=self.user_id, best=0, username="champ")

        # init board
        for i in range(0, len(self.fix_data)):
            self.usecase.board.append(Card(number=self.fix_data[i]))

    def test_create_board(self):
        board = self.usecase.create_board(self.mock_user)
        # check size must be equal to board config size
        self.assertEqual(len(board), BOARD_ROW * BOARD_COL)

        # check max number in board
        max_number = (BOARD_ROW * BOARD_COL) / 2
        for i in range(0, len(board)):
            if board[i].number > max_number:
                raise Exception("number in board is not correct")

        self.redis_mock_repo.set_board.assert_called()

    def test_open_a_card(self):

        self.usecase.open_card(OpenCardRequest(user_id=self.mock_user.id, row=0, col=0))

        self.assertEqual(self.usecase.click, 1)
        self.assertEqual(self.usecase.board[0].is_open, True)

    def test_open_card_matched(self):
        self.usecase.open_card(OpenCardRequest(user_id=self.mock_user.id, row=0, col=0))
        self.usecase.open_card(OpenCardRequest(user_id=self.mock_user.id, row=0, col=2))

        self.assertEqual(self.usecase.click, 2)
        self.assertEqual(self.usecase.board[0].is_open, True)
        self.assertEqual(self.usecase.board[2].is_open, True)
        self.assertEqual(self.usecase.board[2].is_match, True)
        self.assertEqual(self.usecase.board[2].is_match, True)

    def test_open_card_unmatched(self):
        self.usecase.open_card(OpenCardRequest(user_id=self.mock_user.id, row=0, col=0))
        self.usecase.open_card(OpenCardRequest(user_id=self.mock_user.id, row=0, col=1))

        self.assertEqual(self.usecase.click, 2)
        self.assertEqual(self.usecase.board[0].is_open, False)
        self.assertEqual(self.usecase.board[1].is_open, False)

    def test_open_card_win(self):
        self.redis_mock_repo.get_global_best = Mock(return_value=GlobalBest(global_best=1))

        self.usecase.open_card(OpenCardRequest(user_id=self.mock_user.id, row=1, col=1))
        self.usecase.open_card(OpenCardRequest(user_id=self.mock_user.id, row=1, col=0))

        self.usecase.open_card(OpenCardRequest(user_id=self.mock_user.id, row=1, col=2))
        self.usecase.open_card(OpenCardRequest(user_id=self.mock_user.id, row=2, col=2))

        self.usecase.open_card(OpenCardRequest(user_id=self.mock_user.id, row=0, col=0))
        self.usecase.open_card(OpenCardRequest(user_id=self.mock_user.id, row=0, col=2))

        self.usecase.open_card(OpenCardRequest(user_id=self.mock_user.id, row=0, col=1))
        self.usecase.open_card(OpenCardRequest(user_id=self.mock_user.id, row=0, col=3))

        self.usecase.open_card(OpenCardRequest(user_id=self.mock_user.id, row=1, col=3))
        self.usecase.open_card(OpenCardRequest(user_id=self.mock_user.id, row=2, col=0))

        self.usecase.open_card(OpenCardRequest(user_id=self.mock_user.id, row=2, col=1))
        self.usecase.open_card(OpenCardRequest(user_id=self.mock_user.id, row=2, col=3))

        self.assertEqual(self.usecase.click, 12)
        self.assertEqual(self.usecase.all_match(), True)

    def test_convert_matrix_index_to_array_index(self):
        count = 0
        for i in range(BOARD_ROW):
            for j in range(BOARD_COL):
                arr_idx = self.usecase._convert_matrix_index_to_array_index(i, j)
                self.assertEqual(arr_idx, count)
                count += 1

    def test_convert_array_index_to_matrix_index(self):
        max_idx = BOARD_ROW * BOARD_COL
        tuple_result = []
        for i in range(BOARD_ROW):
            for j in range(BOARD_COL):
                tuple_result.append((i, j))
        for i in range(0, max_idx):
            row, col = self.usecase._convert_array_index_to_matrix_index(i)
            self.assertEqual(tuple_result[i], (row, col))

    def test_find_unmatched_card(self):
        # not open card
        result_idx = self.usecase._find_unmatched_card()
        self.assertEqual(-1, result_idx)

        # open one card
        self.usecase.board[0].is_open = True
        result_idx = self.usecase._find_unmatched_card()
        self.assertEqual(0, result_idx)

        # match card
        self.usecase.board[0].is_match = True
        self.usecase.board[3].is_open = True
        self.usecase.board[3].is_match = True
        result_idx = self.usecase._find_unmatched_card()
        self.assertEqual(-1, result_idx)

        # match and non-match
        self.usecase.board[4].is_open = True
        result_idx = self.usecase._find_unmatched_card()
        self.assertEqual(4, result_idx)

    def test_all_match(self):
        for i in range(len(self.usecase.board)):
            self.usecase.board[i].is_match = True
            if i == len(self.usecase.board) - 1:
                self.assertTrue(self.usecase.all_match())
            else:
                self.assertFalse(self.usecase.all_match())

    def test_get_board(self):
        self.redis_mock_repo.get_board = Mock(return_value=None)
        try:
            self.usecase.get_board("test")
        except Exception as e:
            self.assertEqual(e.args[0], ERROR_NOT_FOUND_BOARD)

    def test_resume_board_redis_case(self):
        board = [Card(number=1, is_open=True, is_match=True), Card(number=2, is_open=True),
                 Card(number=1, is_open=True, is_match=True), Card(number=2)]
        click = 3
        self.redis_mock_repo.get_board = Mock(return_value=RedisBoard(board=board, click=click, id=uuid.uuid4()))
        resume_board: ResumeBoard = self.usecase.resume_board(self.mock_user)
        self.assertEqual(self.usecase.board, board)
        self.assertEqual(self.usecase.click, click)
        self.assertEqual(len(resume_board.board), 3)
        self.assertEqual(resume_board.click, 3)

    def test_resume_board_log_repo_case(self):
        self.usecase.board = []
        self.redis_mock_repo.get_board = Mock(return_value=None)
        self.usecase._log_repo.get_board_and_action_log = Mock(
            return_value=BoardAndAction(board_id=uuid.uuid4(), user_id=uuid.uuid4(),
                                        board_data="4,2,4,2,3,3,5,6,6,1,5,1", status=True,
                                        actions=[Action(number=4, arr_idx=0), Action(number=4, arr_idx=2),
                                                 Action(number=4, arr_idx=1), Action(number=5, arr_idx=6)]))
        resume_board: ResumeBoard = self.usecase.resume_board(self.mock_user)

        self.assertEqual(len(resume_board.board), 2)
        self.assertEqual(resume_board.click, 4)

        self.usecase.get_from_board_log = Mock(return_value=[])
        try:
            self.usecase.resume_board(self.mock_user)
        except Exception as e:
            self.assertEqual(e.args[0], ERROR_NOT_FOUND_BOARD)

    def test_get_from_board_log(self):
        # reset current board id
        self.usecase.id = None
        # not found in log do noting
        self.usecase._log_repo.get_board_and_action_log = Mock(return_value=None)
        self.usecase.get_from_board_log("champ")
        self.assertEqual(self.usecase.id, None)

        # found in log but incorrect row col not the same not parse board to usecase
        self.usecase._log_repo.get_board_and_action_log = Mock(
            return_value=BoardAndAction(board_id=uuid.uuid4(), user_id=uuid.uuid4(),
                                        board_data="1,2,3,4", status=True,
                                        actions=[]))
        self.usecase.get_from_board_log("champ")
        self.assertEqual(self.usecase.id, None)

        # found and row col same assign board id
        self.usecase._log_repo.get_board_and_action_log = Mock(
            return_value=BoardAndAction(board_id=self.board_id, user_id=self.user_id,
                                        board_data="4,2,4,2,3,3,5,6,6,1,5,1", status=True,
                                        actions=[]))
        self.usecase.get_from_board_log("champ")
        self.assertEqual(self.usecase.id, self.board_id)

        # load action into board
        self.usecase._log_repo.get_board_and_action_log = Mock(
            return_value=BoardAndAction(board_id=self.board_id, user_id=self.user_id,
                                        board_data="4,2,4,2,3,3,5,6,6,1,5,1", status=True,
                                        actions=[Action(number=4, arr_idx=0), Action(number=4, arr_idx=2)]))
        self.usecase.get_from_board_log("champ")
        self.assertEqual(self.usecase.id, self.board_id)
        self.assertEqual(self.usecase.board[0], Card(number=4, is_open=True, is_match=True))
        self.assertEqual(self.usecase.board[2], Card(number=4, is_open=True, is_match=True))
