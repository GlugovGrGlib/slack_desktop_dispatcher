up:
	source .env; docker compose up -d

rebuild:
	source .env; docker compose up -d --build

down:
	docker compose down -v

revision:
	source .env; alembic revision --autogenerate

migrate:
	source .env; alembic upgrade head
