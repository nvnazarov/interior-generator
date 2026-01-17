from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from app.core.plan.models import Content, Plan, Quota
from app.core.plan.service import IPlansRepository, IPlansUnitOfWork, IQuotaRepository


class QuotaRepository(IQuotaRepository):
    _get_stmt = text(
        "SELECT current_plans_count, max_plans_count, version "
        "FROM projects.plans_per_project_quota "
        "WHERE project_id = :project_id"
    )
    _save_stmt = text(
        "INSERT INTO projects.plans_per_project_quota(project_id, current_plans_count, max_plans_count, version) "
        "VALUES (:project_id, :current_plans_count, :max_plans_count, :version) "
        "ON CONFLICT (project_id) DO UPDATE SET "
        "   max_plans_count = excluded.max_plans_count, "
        "   current_plans_count = excluded.current_plans_count, "
        "   version = excluded.version + 1 "
        "WHERE projects.plans_per_project_quota.version = :version"
    )

    def __init__(self, connection: AsyncConnection):
        self._connection = connection

    async def get(self, project_id: UUID) -> Quota | None:
        cursor = await self._connection.execute(
            self._get_stmt, {"project_id": project_id}
        )
        if (row := cursor.one_or_none()) is None:
            return None
        else:
            return Quota(
                project_id=project_id,
                current_plans_count=row[0],
                max_plans_count=row[1],
                version=row[2],
            )

    async def save(self, quota: Quota) -> None:
        cursor = await self._connection.execute(self._save_stmt, quota.model_dump())
        if cursor.rowcount == 0:
            raise RuntimeError("db error: version conflict")


class PlansRepository(IPlansRepository):
    _delete_stmt = text("UPDATE projects.plans SET deleted = true WHERE id = :plan_id")
    _save_stmt = text(
        "INSERT INTO projects.plans(id, project_id, shell_id, name, version, content, updated_at, created_at) "
        "VALUES (:id, :project_id, :shell_id, :name, :version, :content, :updated_at, :created_at) "
        "ON CONFLICT (id) DO UPDATE SET "
        "   name = excluded.name, "
        "   version = excluded.version, "
        "   content = excluded.content, "
        "   updated_at = excluded.updated_at, "
        "   created_at = excluded.created_at"
    )
    _save_no_content_stmt = text(
        "INSERT INTO projects.plans(id, project_id, shell_id, name, updated_at, created_at) "
        "VALUES (:id, :project_id, :shell_id, :name, :updated_at, :created_at) "
        "ON CONFLICT (id) DO UPDATE SET "
        "   name = excluded.name, "
        "   updated_at = excluded.updated_at, "
        "   created_at = excluded.created_at"
    )
    _save_content_stmt = text(
        "UPDATE projects.plans SET"
        "   version = :version + 1, "
        "   content = :content, "
        "   updated_at = :updated_at, "
        "   created_at = :created_at "
        "WHERE id = :id AND version = :version"
    )
    _get_stmt = text(
        "SELECT pl.project_id, pl.shell_id, pl.name, pl.version, pl.content, pl.created_at, pl.updated_at "
        "FROM projects.plans AS pl "
        "INNER JOIN projects.projects AS pr ON pr.id = pl.project_id "
        "WHERE "
        "   pl.id = :plan_id "
        "   AND pr.account_id = :account_id "
        "   AND pl.deleted = false"
    )
    _get_no_content_stmt = text(
        "SELECT pl.project_id, pl.shell_id, pl.name, pl.created_at, pl.updated_at "
        "FROM projects.plans AS pl "
        "INNER JOIN projects.projects AS pr ON pr.id = pl.project_id "
        "WHERE "
        "   pl.id = :plan_id "
        "   AND pr.account_id = :account_id "
        "   AND pl.deleted = false"
    )
    _get_all_no_content_stmt = text(
        "SELECT pl.id, pl.shell_id, pl.name, pl.created_at, pl.updated_at "
        "FROM projects.plans AS pl "
        "INNER JOIN projects.projects AS pr ON pr.id = :project_id "
        "WHERE "
        "   pl.project_id = :project_id "
        "   AND pr.account_id = :account_id "
        "   AND pl.deleted = false"
    )
    _is_project_owned_by_account = text(
        "SELECT 1 "
        "FROM projects.projects "
        "WHERE id = :project_id AND account_id = :account_id"
    )
    _dummy_content = Content()

    def __init__(self, connection: AsyncConnection):
        self._connection = connection

    async def get(self, plan_id: UUID, account_id: UUID) -> Plan | None:
        cursor = await self._connection.execute(
            self._get_stmt, {"plan_id": plan_id, "account_id": account_id}
        )
        if (row := cursor.one_or_none()) is None:
            return None
        else:
            return Plan(
                id=plan_id,
                project_id=row[0],
                shell_id=row[1],
                name=row[2],
                version=row[3],
                content=Content(**row[4]),
                created_at=row[5],
                updated_at=row[6],
            )

    async def get_no_content(self, plan_id: UUID, account_id: UUID) -> Plan | None:
        cursor = await self._connection.execute(
            self._get_no_content_stmt, {"plan_id": plan_id, "account_id": account_id}
        )
        if (row := cursor.one_or_none()) is None:
            return None
        else:
            return Plan(
                id=plan_id,
                project_id=row[0],
                shell_id=row[1],
                version=0,
                content=self._dummy_content,
                name=row[2],
                created_at=row[3],
                updated_at=row[4],
            )

    async def save(self, plan: Plan) -> None:
        _ = await self._connection.execute(
            self._save_stmt,
            {
                **plan.model_dump(exclude=set(["content"])),
                "content": plan.content.model_dump_json(),
            },
        )

    async def save_content(self, plan: Plan) -> None:
        cursor = await self._connection.execute(
            self._save_content_stmt,
            {
                "id": plan.id,
                "version": plan.version,
                "content": plan.content.model_dump_json(),
                "updated_at": plan.updated_at,
                "created_at": plan.created_at,
            },
        )
        if cursor.rowcount == 0:
            raise
        plan.version += 1

    async def save_no_content(self, plan: Plan) -> None:
        _ = await self._connection.execute(
            self._save_no_content_stmt,
            plan.model_dump(exclude=set(["content"])),
        )

    async def get_all_no_content(
        self, project_id: UUID, account_id: UUID
    ) -> list[Plan]:
        cursor = await self._connection.execute(
            self._get_all_no_content_stmt,
            {"project_id": project_id, "account_id": account_id},
        )
        return list(
            map(
                lambda row: Plan(
                    id=row[0],
                    project_id=project_id,
                    shell_id=row[1],
                    version=0,
                    content=self._dummy_content,
                    name=row[2],
                    created_at=row[3],
                    updated_at=row[4],
                ),
                cursor,
            )
        )

    async def delete(self, plan_id: UUID) -> None:
        await self._connection.execute(self._delete_stmt, {"plan_id": plan_id})

    async def is_project_owned_by_account(
        self, project_id: UUID, account_id: UUID
    ) -> bool:
        cursor = await self._connection.execute(
            self._is_project_owned_by_account,
            {"project_id": project_id, "account_id": account_id},
        )
        return cursor.scalar() is not None


class PlansUnitOfWork(IPlansUnitOfWork):
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
        self.plans = PlansRepository(self._connection)
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
