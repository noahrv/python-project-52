install:
	uv run pip install --upgrade pip
	uv run pip install .

collectstatic:
	uv run python manage.py collectstatic --noinput

migrate:
	uv run python manage.py migrate

build:
	./build.sh

render-start:
	uv run gunicorn task_manager.wsgi