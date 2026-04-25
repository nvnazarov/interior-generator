# projects

## Responsibility

The service defines API for exporting projects into PDF.

## Project structure

- `/app` contains project's source code
- `/docker` contains Dockerfiles
- `/tests` contains tests

## Tech Stack

- Python3
- [uv](https://docs.astral.sh/uv/)
- FastAPI, reportlab, ezdxf

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
MOD=dev
PORT=8080
EXPORTER__API__HOST=0.0.0.0
EXPORTER__API__PORT=80
EXPORTER__API__HEADER_FOR_ACCOUNT_ID=x-account-id
EXPORTER__API_GATEWAY__BASE_URL=http://gateway:8001
EXPORTER__LOGGING__LEVEL=INFO
```
