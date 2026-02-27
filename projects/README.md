# projects

## Responsibility

The service defines API for managing projects and plans. A user can
perform the following operations:

- Create, read, update, and delete a project
- Create, read, update, and delete a plan
- Get a list of all owned projects
- Get a list of all project's plans

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
mod=dev
port=8080
projects__api__host=0.0.0.0
projects__api__port=8080
projects__api__header_for_account_id=x-account-id
projects__general__plans_limit=20
projects__general__projects_limit=20
projects__postgres__host=postgres
projects__postgres__port=5432
projects__postgres__db=postgres
projects__postgres__user=postgres
projects__postgres__password=***
# projects__postgres__password_file=/path/to/password/file
projects__logging__level=INFO
```
