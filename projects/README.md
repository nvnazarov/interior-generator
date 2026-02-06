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

Install Make and Docker.

```sh
make test   # run all tests
make up     # start docker compose
make down   # finish docker compose
```
