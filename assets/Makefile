format:
	@uv run ruff format
	@uv run isort app/ tests/ migrations/

lint:
	@uv run ruff check

qa: lint format
