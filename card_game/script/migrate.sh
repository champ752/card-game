poetry run alembic init migrations

poetry run alembic revision --autogenerate -m 'add users table'

poetry run alembic upgrade head