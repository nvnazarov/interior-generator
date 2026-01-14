from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from app.core.plan.models import Content, Plan, Quota
from app.core.plan.service import IPlansRepository, IPlansUnitOfWork, IQuotaRepository


class QuotaRepository(IQuotaRepository):
    _get_stmt = text(
        "SELECT current_plans_count, max_plans_count, version "
        "FROM plans_per_project_quota "
        "WHERE project_id = :project_id"
    )
    _save_stmt = text(
        "UPDATE plans_per_project_quota SET "
        "current_plans_count = :current_plans_count, "
        "max_plans_count = :max_plans_count, "
        "version = version + 1 "
        "WHERE project_id = :project_id AND version = :version"
    )

    def __init__(self, connection: AsyncConnection):
        self._connection = connection

    async def get(self, project_id: UUID) -> Quota:
        cursor = await self._connection.execute(
            self._get_stmt, {"project_id": project_id}
        )
        if (row := cursor.one_or_none()) is None:
            raise RuntimeError("db error: db returned null, expected a quota row")
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
    _delete_stmt = text("UPDATE plans SET deleted = true WHERE id = :plan_id")
    _save_stmt = text(
        "INSERT INTO plans(id, name, version, content, updated_at) VALUES "
        "(:plan_id, :name, :version, :content, now()) "
        "ON CONFLICT (id) DO UPDATE SET "
        "name = excluded.name, "
        "version = excluded.version, "
        "content = excluded.content, "
        "updated_at = now()"
    )
    _save_no_content_stmt = text(
        "INSERT INTO plans(id, name, updated_at) VALUES "
        "(:plan_id, :name, now()) "
        "ON CONFLICT (id) DO UPDATE SET "
        "name = excluded.name, "
        "updated_at = now()"
    )
    _get_stmt = text(
        "SELECT pl.id, pl.name, pl.version, pl.content, pl.created_at, pl.updated_at "
        "FROM plans AS pl "
        "INNER JOIN projects AS pr ON pr.id = pl.project_id "
        "WHERE "
        "pl.id = :plan_id "
        "AND pr.account_id = :account "
        "AND pl.deleted = false"
    )
    _get_no_content_stmt = text(
        "SELECT pl.id, pl.name, pl.created_at, pl.updated_at "
        "FROM plans AS pl "
        "INNER JOIN projects AS pr ON pr.id = pl.project_id "
        "WHERE "
        "pl.id = :plan_id "
        "AND pr.account_id = :account "
        "AND pl.deleted = false"
    )
    _get_all_no_content_stmt = text(
        "SELECT pl.id, pl.name, pl.created_at, pl.updated_at "
        "FROM plans AS pl "
        "INNER JOIN projects AS pr ON pr.id = :project_id "
        "WHERE "
        "pl.project_id = :project_id "
        "AND pr.account_id = :account "
        "AND pl.deleted = false"
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
                content=Content(
                    version=row[1],
                    **row[2],
                ),
                name=row[3],
                created_at=row[4],
                updated_at=row[5],
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
                content=self._dummy_content,
                name=row[3],
                created_at=row[4],
                updated_at=row[5],
            )

    async def save(self, plan: Plan) -> None:
        _ = await self._connection.execute(self._save_stmt, plan.model_dump())

    async def save_no_content(self, plan: Plan) -> None:
        _ = await self._connection.execute(
            self._save_no_content_stmt, plan.model_dump()
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
                    content=self._dummy_content,
                    name=row[1],
                    created_at=row[2],
                    updated_at=row[3],
                ),
                cursor,
            )
        )

    async def delete(self, plan_id: UUID) -> None:
        await self._connection.execute(self._delete_stmt, {"plan_id": plan_id})


class PlansUnitOfWork(IPlansUnitOfWork):
    def __init__(
        self,
        engine: AsyncEngine,
    ):
        self._engine = engine
        self._connection: AsyncConnection | None = None

    async def __aenter__(self):
        self._connection = self._engine.connect()
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
