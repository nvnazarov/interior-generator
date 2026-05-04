test:
	@uv run pytest

test-unit:
	@uv run pytest -m "unit" -vv

test-integration:
	@uv run pytest -m "integration" -vv

format:
	@uv run ruff format
	@uv run isort app/ tests/

local:
	@uv run python -m app.main

up:
	@docker compose up --build

lint:
	@uv run ruff check

qa: lint format
