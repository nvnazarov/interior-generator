# Catalog

## Responsibility

The catalog stores meta-information about furniture and other
interior elements. This information includes:

1. Unique furniture ID
2. Furniture name
3. Dimensions (width, height, depth)
4. Links to resources (thumbnail, image, 3D model)
5. Mount type (floor, ceiling, wall, etc.)
6. Other information

The catalog allows to search furniture by ID, name, area it usually
belongs to (kitchen, bathroom, etc.), and description.

## Project structure

- `/app` contains project's source code
- `/docker` contains Dockerfiles
- `/migrations` contains scripts for running database migrations
- `/seeder` contains scripts for seeding the database
- `/tests` contains tests

## Tech Stack

- Python 3
- [uv](https://docs.astral.sh/uv/)
- fastapi, elasticsearch

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

make migrate            # Run Elastic index migration
make seed               # Seed Elastic with furniture data

make local              # Start the program locally
make up                 # Start the program in Docker Compose
```
