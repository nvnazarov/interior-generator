from typing import Any, AsyncContextManager
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection
from sqlalchemy import text

from projects.core.errors import ProjectNotFoundError
from projects.core.models import Project
from projects.core.service import IProjectUnitOfWork


class ProjectUnitOfWork(IProjectUnitOfWork):
    def __init__(self, connection: AsyncConnection):
        self.connection = connection

    async def create_project(self, account_id: UUID) -> Project:
        stmt = text(
            "INSERT INTO projects.projects(account_id) "
            "VALUES (:account_id)"
            "RETURNING id, name, description, pinned, created_at, updated_at"
        )
        result = await self.connection.execute(stmt, {"account_id": account_id})
        if (row := result.first()) is None:
            raise RuntimeError("unknown db error")
        else:
            return Project(
                id=row[0],
                account_id=account_id,
                name=row[1],
                description=row[2],
                pinned=row[3],
                created_at=row[4],
                updated_at=row[5],
            )

    async def get_project_by_id(
        self, account_id: UUID, project_id: UUID
    ) -> Project | None:
        stmt = text(
            "SELECT name, description, pinned, created_at, updated_at "
            "FROM projects.projects "
            "WHERE account_id = :account_id AND id = :project_id AND deleted = false"
        )
        result = await self.connection.execute(
            stmt, {"account_id": account_id, "project_id": project_id}
        )
        if (row := result.first()) is None:
            return None
        else:
            return Project(
                id=project_id,
                account_id=account_id,
                name=row[0],
                description=row[1],
                pinned=row[2],
                created_at=row[3],
                updated_at=row[4],
            )

    async def delete_project(self, account_id: UUID, project_id: UUID) -> None:
        stmt = text(
            "UPDATE projects.projects "
            "SET deleted = true "
            "WHERE account_id = :account_id AND id = :project_id"
        )
        _ = await self.connection.execute(
            stmt, {"account_id": account_id, "project_id": project_id}
        )

    async def patch_project(
        self, account_id: UUID, project_id: UUID, **kwargs: Any
    ) -> None:
        kwargs = dict(
            filter(lambda arg: arg[0] in ["name", "description"], kwargs.items())
        )
        set_clause = ", ".join(map(lambda arg: f"{arg[0]} = :{arg[0]}", kwargs.items()))
        stmt = text(
            "UPDATE projects.projects "
            f"SET {set_clause} "
            "WHERE account_id = :account_id AND id = :project_id AND deleted = false"
        )
        result = await self.connection.execute(
            stmt, {"account_id": account_id, "project_id": project_id, **kwargs}
        )
        if result.rowcount == 0:
            raise ProjectNotFoundError

    async def get_all_projects(self, account_id: UUID) -> list[Project]:
        raise NotImplementedError

    async def pin_project(self, account_id: UUID, project_id: UUID) -> None:
        stmt = text(
            "UPDATE projects.projects "
            "SET pinned = true "
            "WHERE account_id = :account_id AND id = :project_id AND deleted = false"
        )
        result = await self.connection.execute(
            stmt, {"account_id": account_id, "project_id": project_id}
        )
        if result.rowcount == 0:
            raise ProjectNotFoundError

    async def unpin_project(self, account_id: UUID, project_id: UUID) -> None:
        stmt = text(
            "UPDATE projects.projects "
            "SET pinned = false "
            "WHERE account_id = :account_id AND id = :project_id AND deleted = false"
        )
        result = await self.connection.execute(
            stmt, {"account_id": account_id, "project_id": project_id}
        )
        if result.rowcount == 0:
            raise ProjectNotFoundError

    async def get_total_projects_count(self, account_id: UUID) -> int:
        stmt = text(
            "SELECT count(*) "
            "FROM projects.projects "
            "WHERE account_id = :account_id AND deleted = false"
        )
        result = await self.connection.execute(stmt, {"account_id": account_id})
        if (row := result.first()) is None:
            raise RuntimeError("unknown db error")
        else:
            return int(row[0])

    async def commit(self) -> None:
        await self.connection.commit()


class ProjectUnitOfWorkFactory:
    def __init__(self, url: str):
        self.engine = create_async_engine(url)

    def __call__(self) -> AsyncContextManager[ProjectUnitOfWork]:
        return self._factory()

    @asynccontextmanager
    async def _factory(self):
        async with self.engine.connect() as connection:
            yield ProjectUnitOfWork(connection)
