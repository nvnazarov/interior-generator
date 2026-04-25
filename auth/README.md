# auth

## Responsibility

The service defines API for managing accounts, such as:

- Create (register) or delete an account
- Enter (login) into account
- Update accounts info (name, avatar, etc.)

## Project structure

- `/src` contains project's source code
- `/prisma` contains database schema for Prisma
- `/docker` contains Dockerfiles

## Tech Stack

- Node 20
- Typescript
- Prisma
- express.js
- better-auth

## Setup

Install Make and Docker.

```sh
make test       # run all tests
make up         # start docker compose
make format     # format the code
```
