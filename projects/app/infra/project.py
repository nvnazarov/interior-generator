from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from app.core.project.models import Project, Quota
from app.core.project.service import (
    IProjectsRepository,
    IProjectsUnitOfWork,
    IQuotaRepository,
)


class QuotaRepository(IQuotaRepository):
    _get_stmt = text(
        "SELECT current_projects_count, max_projects_count, version "
        "FROM projects.projects_quota "
        "WHERE account_id = :account_id"
    )
    _save_stmt = text(
        "INSERT INTO projects.projects_quota(account_id, current_projects_count, max_projects_count, version) "
        "VALUES (:account_id, :current_projects_count, :max_projects_count, :version) "
        "ON CONFLICT (account_id) DO UPDATE SET "
        "   max_projects_count = excluded.max_projects_count, "
        "   current_projects_count = excluded.current_projects_count, "
        "   version = excluded.version + 1 "
        "WHERE projects.projects_quota.version = :version"
    )

    def __init__(self, connection: AsyncConnection):
        self._connection = connection

    async def get(self, account_id: UUID) -> Quota | None:
        cursor = await self._connection.execute(
            self._get_stmt, {"account_id": account_id}
        )
        if (row := cursor.one_or_none()) is None:
            return None
        else:
            return Quota(
                account_id=account_id,
                current_projects_count=row[0],
                max_projects_count=row[1],
                version=row[2],
            )

    async def save(self, quota: Quota) -> None:
        cursor = await self._connection.execute(self._save_stmt, quota.model_dump())
        if cursor.rowcount == 0:
            raise RuntimeError("db error: version conflict")


class ProjectsRepository(IProjectsRepository):
    _save_stmt = text(
        "INSERT INTO projects.projects(id, account_id, name, description, pinned, updated_at, created_at) "
        "VALUES (:id, :account_id, :name, :description, :pinned, :updated_at, :created_at) "
        "ON CONFLICT (id) DO UPDATE SET "
        "   account_id = excluded.account_id, "
        "   name = excluded.name, "
        "   description = excluded.description, "
        "   pinned = excluded.pinned, "
        "   updated_at = excluded.updated_at, "
        "   created_at = excluded.created_at "
        "WHERE projects.projects.id = :id"
    )
    _delete_stmt = text(
        "UPDATE projects.projects SET deleted = true WHERE id = :project_id"
    )
    _get_stmt = text(
        "SELECT account_id, name, description, pinned, created_at, updated_at "
        "FROM projects.projects WHERE id = :project_id AND deleted = false"
    )
    _all_stmt = text(
        "SELECT id, name, description, pinned, created_at, updated_at "
        "FROM projects.projects WHERE account_id = :account_id AND deleted = false"
    )

    def __init__(self, connection: AsyncConnection):
        self._connection = connection

    async def get(self, project_id: UUID) -> Project | None:
        cursor = await self._connection.execute(
            self._get_stmt, {"project_id": project_id}
        )
        if (row := cursor.one_or_none()) is None:
            return None
        else:
            return Project(
                id=project_id,
                account_id=row[0],
                name=row[1],
                description=row[2],
                pinned=row[3],
                created_at=row[4],
                updated_at=row[5],
            )

    async def save(self, project: Project) -> None:
        await self._connection.execute(self._save_stmt, project.model_dump())

    async def delete(self, project_id: UUID) -> None:
        await self._connection.execute(self._delete_stmt, {"project_id": project_id})

    async def all(self, account_id: UUID) -> list[Project]:
        cursor = await self._connection.execute(
            self._all_stmt, {"account_id": account_id}
        )
        projects = list(
            map(
                lambda row: Project(
                    id=row[0],
                    account_id=account_id,
                    name=row[1],
                    description=row[2],
                    pinned=row[3],
                    created_at=row[4],
                    updated_at=row[5],
                ),
                cursor,
            )
        )
        return projects


class ProjectsUnitOfWork(IProjectsUnitOfWork):
    def __init__(
        self,
        engine: AsyncEngine,
    ):
        self._engine = engine
        self._connection: AsyncConnection | None = None

    async def __aenter__(self):
        self._connection = self._engine.connect()
        await self._connection.start()
        self.quota = QuotaRepository(self._connection)
        self.projects = ProjectsRepository(self._connection)
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, traceback: Any):
        try:
            if exc:
                await self.rollback()
            else:
                await self.commit()
        finally:
            if self._connection:
                await self._connection.close()

    async def commit(self) -> None:
        if self._connection:
            await self._connection.commit()

    async def rollback(self) -> None:
        if self._connection:
            await self._connection.rollback()
