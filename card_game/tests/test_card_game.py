import unittest
from unittest import mock
from unittest.mock import MagicMock

from card_game import __version__
from card_game.configs.config import BOARD_COL, BOARD_ROW
from card_game.schemas.card import Card, OpenCardRequest
from card_game.usecase.game_usecase import GameUsecase


def test_version():
    assert __version__ == '0.1.0'


class TestUsecase(unittest.TestCase):
    @mock.patch('card_game.repositories.redis_repository.RedisRepository')
    def setUp(self, repo):
        self.repo = repo
        self.usecase = GameUsecase(self.repo, MagicMock())
        self.fix_data = [4, 2, 4, 2, 3, 3, 5, 6,
                         6, 1, 5, 1]

    def test_create_board(self):
        board = self.usecase.create_board("champ")
        # check size must be equal to board config size
        self.assertEqual(len(board), BOARD_ROW * BOARD_COL)

        # check max number in board
        max_number = (BOARD_ROW * BOARD_COL) / 2
        for i in range(0, len(board)):
            if board[i].number > max_number:
                raise Exception("number in board is not correct")

        self.repo.set_board.assert_called()

    def test_open_a_card(self):
        for i in range(0, len(self.fix_data)):
            self.usecase.board.append(Card(number=self.fix_data[i]))
        self.usecase.open_card(OpenCardRequest(username="champ", row=0, col=0))

        self.assertEqual(self.usecase.click, 1)
        self.assertEqual(self.usecase.board[0].is_open, True)

    def test_open_card_matched(self):
        for i in range(0, len(self.fix_data)):
            self.usecase.board.append(Card(number=self.fix_data[i]))
        self.usecase.open_card(OpenCardRequest(username="champ", row=0, col=0))
        self.usecase.open_card(OpenCardRequest(username="champ", row=0, col=2))

        self.assertEqual(self.usecase.click, 2)
        self.assertEqual(self.usecase.board[0].is_open, True)
        self.assertEqual(self.usecase.board[2].is_open, True)
        self.assertEqual(self.usecase.board[2].is_match, True)
        self.assertEqual(self.usecase.board[2].is_match, True)

    def test_open_card_unmatched(self):
        for i in range(0, len(self.fix_data)):
            self.usecase.board.append(Card(number=self.fix_data[i]))
        self.usecase.open_card(OpenCardRequest(username="champ", row=0, col=0))
        self.usecase.open_card(OpenCardRequest(username="champ", row=0, col=1))

        self.assertEqual(self.usecase.click, 2)
        self.assertEqual(self.usecase.board[0].is_open, False)
        self.assertEqual(self.usecase.board[1].is_open, False)

    def test_open_card_win(self):
        for i in range(0, len(self.fix_data)):
            self.usecase.board.append(Card(number=self.fix_data[i]))

        self.usecase.open_card(OpenCardRequest(username="champ", row=1, col=1))
        self.usecase.open_card(OpenCardRequest(username="champ", row=1, col=0))

        self.usecase.open_card(OpenCardRequest(username="champ", row=1, col=2))
        self.usecase.open_card(OpenCardRequest(username="champ", row=2, col=2))

        self.usecase.open_card(OpenCardRequest(username="champ", row=0, col=0))
        self.usecase.open_card(OpenCardRequest(username="champ", row=0, col=2))

        self.usecase.open_card(OpenCardRequest(username="champ", row=0, col=1))
        self.usecase.open_card(OpenCardRequest(username="champ", row=0, col=3))

        self.usecase.open_card(OpenCardRequest(username="champ", row=1, col=3))
        self.usecase.open_card(OpenCardRequest(username="champ", row=2, col=0))

        self.usecase.open_card(OpenCardRequest(username="champ", row=2, col=1))
        self.usecase.open_card(OpenCardRequest(username="champ", row=2, col=3))

        self.assertEqual(self.usecase.click, 12)
        self.assertEqual(self.usecase.all_match(), True)
