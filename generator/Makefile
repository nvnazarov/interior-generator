test:
	@uv run pytest ./tests

test-unit:
	@uv run pytest -m "unit" ./tests -vv

test-integration:
	@uv run pytest -m "integration" ./tests -vv

local:
	@uv run python -m app.main

up:
	@docker compose up --build

migration:
	@uv run alembic upgrade head --sql

format:
	@uv run ruff format
	@uv run isort app/ tests/

lint:
	@uv run ruff check

qa: lint format
