import unittest
from unittest import mock
from unittest.mock import MagicMock, Mock

from poetry import __version__

from card_game.constant.constant import ERROR_USER_ALREADY_REGISTERED
from card_game.schemas.user import UserCreate
from card_game.usecase.user_usecase import UserUsecase

def test_version():
    assert __version__ == '0.1.0'


class TestGameUsecase(unittest.TestCase):
    def setUp(self):
        self._mock_user_repo = MagicMock()
        self.usecase = UserUsecase(self._mock_user_repo)

    def test_create_user(self):
        # test create user normal flow
        self.usecase._user_repository.get_user_by_username = Mock(return_value=None)
        self.usecase.get_password_hash = Mock(return_value="")
        self.usecase.create_user(UserCreate(username="champ", password="password"))
        self._mock_user_repo.create_user.assert_called_once()

        # test create user with user already exist
        self._mock_user_repo.get_user_by_username(return_value="champ")
        try:
            self.usecase.create_user(UserCreate(username="champ", password="password"))
        except Exception as e:
            self.assertEqual(e.args[0], ERROR_USER_ALREADY_REGISTERED)


