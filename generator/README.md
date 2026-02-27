# generator

## Responsibility

The service defined API for automatic plans generation based on
natural language processing.

## Project structure

- `/app` contains project's source code
- `/docker` contains Dockerfiles
- `/migrations` contains database migration scripts
- `/tests` contains tests

## Tech Stack

- Python3
- [uv](https://docs.astral.sh/uv/)
- FastAPI, Alembic, SQLAlchemy

## Setup

Install Make and Docker. Use the following commands:

```bash
make test               # run all tests
make test-unit          # run unit tests
make test-integration   # run integration tests

make format             # run code formatter
make lint               # run code linter
make qa                 # run code formatter and linter

make local              # start the program locally
make up                 # start the program in docker compose
```

Environment:

```dotenv
mod=dev
port=8080
generator__api__host=0.0.0.0
generator__api__port=80
generator__api__header_for_account_id=x-account-id
generator__openai__api_key=***
generator__openai__base_url=***
generator__logging__level=INFO
```
