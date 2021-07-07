import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette import testclient

from card_game.main import app


# client = TestClient(app)


@pytest.fixture
def app() -> FastAPI:
    from card_game.main import get_application  # local import for testing purpose

    return get_application()


@pytest.fixture
def client(app: FastAPI):
    return TestClient(app)


def test_auth_token(client):
    payload = {'username': "champ", "password": "1234"}
    response = client.post("/api/auth/token", data=payload)
    print(response)
    assert response.status_code == 200
    res = response.json()
    assert res["token_type"]
    assert res["access_token"]


def test_auth_token_failed(client):
    payload = {'username': "a", "password": "a"}
    response = client.post("/api/auth/token", data=payload)
    assert response.status_code == 401
    res = response.json()
    assert res["detail"]
    assert res["detail"][0] == "Incorrect username or password"


def test_auth_token_uncompleted_payload(client):
    payload = {'username': "a"}
    response = client.post("/api/auth/token", data=payload)
    assert response.status_code == 422
    res = response.json()
    assert res["detail"] == ''
    # assert res["detail"][0] == "something went wrong"


# def test_create_duplicate_user(client):
#     payload = {"username": "champ", "password": "0"}
#     response = client.post("/api/user", data=payload)
#     print(response)
#     # assert response.status_code == 422
