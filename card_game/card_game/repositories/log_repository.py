import requests
from pika.adapters.blocking_connection import BlockingChannel

from card_game.configs.config import GO_SERVER_URL
from card_game.schemas.external import BoardAndAction, CreateBoardLog, CreateActionLog


class LogRepository:
    def __init__(self, connection):
        self.connection = connection
        self.channel: BlockingChannel = self.connection.channel()

    def update_board_log_win(self, board_id: str) -> None:
        requests.get(GO_SERVER_URL + "/api/board-win/" + board_id)

    def get_board_and_action_log(self, user_id: str) -> BoardAndAction or None:
        resp = requests.get(GO_SERVER_URL + "/api/board-action/" + user_id)
        print(resp.json())
        if resp.status_code == 200:
            result = BoardAndAction.parse_obj(resp.json())
            return result
        return None

    def create_board_log(self, board_data: CreateBoardLog):
        self.channel.queue_declare("create_board")
        self.channel.basic_publish(
            exchange='',
            routing_key='create_board',
            body=board_data.json()
        )
        self.connection.close()

    def create_action_log(self, action_data: CreateActionLog):
        self.channel.queue_declare("create_action")
        self.channel.basic_publish(
            exchange='',
            routing_key='create_action',
            body=action_data.json()
        )
        self.connection.close()
