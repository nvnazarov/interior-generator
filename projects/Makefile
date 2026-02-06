test:
	uv run pytest

test-unit:
	uv run pytest -m "unit"

test-integration:
	uv run pytest -m "integration"

up:
	docker compose -f docker-compose.yml up --build
	
migration:
	uv run alembic upgrade head --sql
