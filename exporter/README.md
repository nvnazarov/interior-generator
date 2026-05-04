# projects

## Responsibility

The service defines API for exporting projects into PDF.

## Project structure

- `/app` contains project's source code
- `/docker` contains Dockerfiles
- `/tests` contains tests

## Tech Stack

- Python 3
- [uv](https://docs.astral.sh/uv/)
- fastapi, reportlab, numpy

## Setup

Install uv, make and Docker. Provide a `.env` file (see `.env.example`).
Use the following commands:

```bash
make test               # Run all tests
make test-unit          # Run unit tests
make test-integration   # Run integration tests

make format             # Run code formatter
make lint               # Run code linter
make qa                 # Run code formatter and linter

make local              # Start the program locally
make up                 # Start the program inside Doker Compose
```
