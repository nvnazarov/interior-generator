# projects

## Responsibility

The service defines API for exporting projects and plans into
various file formats, like PDF and DXF.

## Project structure

- `/app` contains project's source code
- `/docker` contains Dockerfiles
- `/tests` contains tests

## Tech Stack

- Python3
- [uv](https://docs.astral.sh/uv/)
- FastAPI, reportlab, ezdxf

## Setup

Install Make and Docker.

```sh
make test   # run all tests
make up     # start docker compose
make down   # finish docker compose
```
