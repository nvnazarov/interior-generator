# auth

## Responsibility

The service defines API for managing accounts and authentication.

## Project structure

- `/src` contains project's source code plus tests (files with `.test.ts` suffix)
- `/prisma` contains Prisma database schema definition and migrations
- `/docker` contains Dockerfiles
- `/tests` contains tests

## Tech Stack

- Node 20
- Typescript
- prisma, pg, express, better-auth

## Setup

Install node, make and Docker. Create a `.env` file (see `.env.example`).
Use the following commands:

```bash
make local      # Run locally
make up         # Run inside Docker Compose

make test       # Run all tests
make format     # Run code formatter

make migrate    # Migrate database schema to the latest version
```
