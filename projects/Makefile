test:
	@uv run pytest

test-unit:
	@uv run pytest -m "unit" -vv

test-integration:
	@uv run pytest -m "integration" -vv

local:
	@uv run python -m app.main

up:
	@docker compose -f docker-compose.yml up --build
	
migration:
	@uv run alembic upgrade head --sql

format:
	@uv run ruff format
	@uv run isort app/ tests/ migrations/

lint:
	@uv run ruff check

qa: lint format
