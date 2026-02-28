# Catalog

## Responsibility

The catalog stores meta-information about furniture and other
interior elements. This information includes:

1. Unique furniture ID
2. Furniture name
3. Dimensions (width, height, depth)
4. Links to resources (thumbnail, image, 3D model)
5. Mount type (floor, ceiling, wall, etc.)
6. Other furniture-specific information (functionality, restrictions)

The catalog allows to search furniture by ID, name, and area it usually
belongs to (kitchen, bathroom, etc.).

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

make migration          # get migration script
```

Environment:

```dotenv
MOD=dev
PORT=8080
CATALOG__API__HOST=0.0.0.0
CATALOG__API__PORT=8080
CATALOG__POSTGRES__HOST=postgres
CATALOG__POSTGRES__PORT=5432
CATALOG__POSTGRES__DB=postgres
CATALOG__POSTGRES__USER=postgres
CATALOG__POSTGRES__PASSWORD=***
# CATALOG__POSTGRES__PASSWORD_FILE=/path/to/password/file
CATALOG__LOGGING__LEVEL=INFO
```
