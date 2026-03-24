# Assets

## Responsibility

The assets service regulates how the assets, e.g. users'
avatars, are accessed and modified.

## Project structure

- `/app` contains project's source code
- `/docker` contains Dockerfiles

## Tech Stack

- Python3
- [uv](https://docs.astral.sh/uv/)
- FastAPI

## Setup

Install Make and Docker. Use the following commands:

```bash
make format             # run code formatter
make lint               # run code linter
make qa                 # run code formatter and linter
```

Environment:

```dotenv
MOD=dev
PORT=8080
ASSETS__API__HOST=0.0.0.0
ASSETS__API__PORT=8080
ASSETS__MINIO__HOST=minio
ASSETS__MINIO__PORT=9000
ASSETS__LOGGING__LEVEL=INFO
```
