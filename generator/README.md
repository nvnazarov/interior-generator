# generator

## Responsibility

The service allows users to generate interior designs based on
textual description.

## Project structure

- `/app` contains project's source code
- `/docker` contains Dockerfiles
- `/migrations` contains database migration scripts
- `/tests` contains tests

## Tech Stack

- Python 3
- [uv](https://docs.astral.sh/uv/)
- fastapi, alembic, sqlalchemy, psycopg, openai, numpy

## Setup

Install uv, make and Docker. Create a `.env` file (see `.env.example`).
Use the following commands:

```bash
make test               # Run all tests
make test-unit          # Run unit tests
make test-integration   # Run integration tests

make format             # Run code formatter
make lint               # Run code linter
make qa                 # Run code formatter and linter

make local              # Start the program locally
make up                 # Start the program in Docker Compose

make migrate            # Migrate database to the latest version
```
