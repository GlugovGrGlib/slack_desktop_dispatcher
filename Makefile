up: run_db run_app

run_app:
	poetry run python desktop_dispatcher/main.py add_dev.yaml

run_db:
	docker run -d -e POSTGRES_DB=add_desktop_dispatcher -e POSTGRES_USER=add_user -e POSTGRES_PASSWORD=add_pass -p 5432:5432 postgres:10
