up: run_db run_app migrate init_db

run_app:
	source secret.env; poetry run python desktop_dispatcher/main.py add_dev.yaml

run_db:
	docker run -d -e POSTGRES_DB=add_desktop_dispatcher -e POSTGRES_USER=add_user -e POSTGRES_PASSWORD=add_pass -p 5432:5432 postgres:10

init_db:
	source secret.env; poetry run python desktop_dispatcher/init_db.py

migrate:
	source secret.env; alembic upgrade head
