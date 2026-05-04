import logging
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy import bindparam, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from app.core.account import Account, AccountsRepository
from app.core.plan import Plan, PlansRepository
from app.core.project import Project, ProjectsRepository
from app.core.unit_of_work import UnitOfWork, UnitOfWorkFactory

logger = logging.getLogger(__name__)


def set_version(obj: Any, version: int):
    setattr(obj, "_pg_version", version)


def get_version(obj: Any) -> int:
    return int(getattr(obj, "_pg_version", 0))


STMT_GET_ACCOUNT_BY_ID = text(
    "SELECT "
    "   projects_count, "
    "   projects_limit, "
    "   version "
    "FROM "
    "   projects.accounts "
    "WHERE "
    "   account_id = :account_id"
)
STMT_SAVE_ACCOUNT = text(
    "INSERT INTO "
    "   projects.accounts(account_id, projects_count, projects_limit, version) "
    "VALUES "
    "   (:account_id, :projects_count, :projects_limit, :version) "
    "ON CONFLICT (account_id) DO UPDATE SET "
    "   projects_count=excluded.projects_count, "
    "   version=excluded.version + 1 "
    "WHERE "
    "   projects.accounts.version = :version"
)
STMT_GET_PROJECT_WITHOUT_CONTENT = text(
    "SELECT "
    "   account_id, "
    "   name, "
    "   revision, "
    "   created_at, "
    "   updated_at, "
    "   plans_count, "
    "   plans_limit, "
    "   published, "
    "   published_at, "
    "   version "
    "FROM "
    "   projects.projects "
    "WHERE "
    "   id = :project_id "
    "   AND NOT deleted"
)
STMT_GET_PROJECT = text(
    "SELECT "
    "   account_id, "
    "   name, "
    "   revision, "
    "   content, "
    "   created_at, "
    "   updated_at, "
    "   plans_count, "
    "   plans_limit, "
    "   published, "
    "   published_at, "
    "   version "
    "FROM "
    "   projects.projects "
    "WHERE "
    "   id = :project_id "
    "   AND NOT deleted"
)
STMT_SAVE_PROJECT = text(
    "INSERT INTO projects.projects("
    "   id, "
    "   account_id, "
    "   name, "
    "   revision, "
    "   content, "
    "   created_at, "
    "   updated_at, "
    "   plans_count, "
    "   plans_limit, "
    "   published, "
    "   published_at, "
    "   version "
    ") "
    "VALUES ( "
    "   :id, "
    "   :account_id, "
    "   :name, "
    "   :revision, "
    "   :content, "
    "   :created_at, "
    "   :updated_at, "
    "   :plans_count, "
    "   :plans_limit, "
    "   :published, "
    "   :published_at, "
    "   :version "
    ") "
    "ON CONFLICT (id) DO UPDATE SET "
    "   account_id = excluded.account_id, "
    "   name = excluded.name, "
    "   revision = excluded.revision, "
    "   content = excluded.content, "
    "   created_at = excluded.created_at, "
    "   updated_at = excluded.updated_at, "
    "   plans_count = :plans_count, "
    "   plans_limit = :plans_limit, "
    "   published = :published, "
    "   published_at = :published_at, "
    "   version = excluded.version + 1 "
    "WHERE "
    "   projects.projects.version = :version"
).bindparams(bindparam("content", type_=JSONB))
STMT_SAVE_PROJECT_WITHOUT_CONTENT = text(
    "UPDATE projects.projects "
    "SET "
    "   account_id = :account_id, "
    "   name = :name, "
    "   revision = :revision, "
    "   created_at = :created_at, "
    "   updated_at = :updated_at, "
    "   plans_count = :plans_count, "
    "   plans_limit = :plans_limit, "
    "   published = :published, "
    "   published_at = :published_at, "
    "   version = :version + 1 "
    "WHERE "
    "   id = :id "
    "   AND version = :version"
)
STMT_DELETE_PROJECT = text(
    "UPDATE projects.projects SET deleted = true WHERE id = :project_id"
)
STMT_GET_ALL_PROJECTS_OWNED_BY_ACCOUNT = text(
    "SELECT "
    "   id, "
    "   name, "
    "   revision, "
    "   created_at, "
    "   updated_at, "
    "   plans_count, "
    "   plans_limit, "
    "   published, "
    "   published_at, "
    "   version "
    "FROM "
    "   projects.projects "
    "WHERE "
    "   account_id = :account_id "
    "   AND NOT deleted "
    "ORDER BY "
    "   created_at DESC"
)
STMT_GET_PLAN = text(
    "SELECT "
    "   project_id, "
    "   name, "
    "   revision, "
    "   content, "
    "   created_at, "
    "   updated_at, "
    "   version "
    "FROM "
    "   projects.plans "
    "WHERE "
    "   id = :plan_id "
    "   AND NOT deleted"
)
STMT_GET_PLAN_WITHOUT_CONTENT = text(
    "SELECT "
    "   id, "
    "   project_id, "
    "   name, "
    "   revision, "
    "   created_at, "
    "   updated_at, "
    "   version "
    "FROM "
    "   projects.plans "
    "WHERE "
    "   id = :plan_id "
    "   AND NOT deleted"
)
STMT_SAVE_PLAN = text(
    "INSERT INTO projects.plans("
    "   id, "
    "   project_id, "
    "   name, "
    "   revision, "
    "   content, "
    "   created_at, "
    "   updated_at, "
    "   version "
    ") VALUES ( "
    "   :id, "
    "   :project_id, "
    "   :name, "
    "   :revision, "
    "   :content, "
    "   :created_at, "
    "   :updated_at, "
    "   :version "
    ") "
    "ON CONFLICT (id) DO "
    "UPDATE SET "
    "   project_id = excluded.project_id, "
    "   name = excluded.name, "
    "   revision = excluded.revision, "
    "   content = excluded.content, "
    "   created_at = excluded.created_at, "
    "   updated_at = excluded.updated_at, "
    "   version = excluded.version + 1 "
).bindparams(bindparam("content", type_=JSONB))
STMT_SAVE_PLAN_WITHOUT_CONTENT = text(
    "UPDATE "
    "   projects.plans "
    "SET "
    "   project_id = :project_id, "
    "   name = :name, "
    "   revision = :revision, "
    "   created_at = :created_at, "
    "   updated_at = :updated_at, "
    "   version = :version + 1 "
    "WHERE "
    "   id = :id "
    "   AND version = :version "
    "   AND NOT deleted"
)
STMT_GET_PLANS_OF_PROJECT = text(
    "SELECT "
    "   id, "
    "   name, "
    "   revision, "
    "   created_at, "
    "   updated_at "
    "FROM "
    "   projects.plans "
    "WHERE "
    "   project_id = :project_id "
    "   AND NOT deleted "
    "ORDER BY "
    "   created_at ASC"
)
STMT_DELETE_PLAN = text(
    "UPDATE "
    "   projects.plans "
    "SET "
    "   deleted = true "
    "WHERE "
    "   id = :plan_id "
    "   AND version = :version"
)


class OptimisticLockError(Exception): ...


class PostgresAccountRepository(AccountsRepository):
    def __init__(self, connection: AsyncConnection):
        self._conn = connection

    async def find(self, account_id: str) -> Account | None:
        cursor = await self._conn.execute(
            STMT_GET_ACCOUNT_BY_ID, {"account_id": account_id}
        )
        if (row := cursor.one_or_none()) is None:
            return None
        else:
            account = Account.create(
                account_id,
                projects_count=row[0],
                projects_limit=row[1],
            )
            set_version(account, int(row[2]))
            return account

    async def save(self, account: Account) -> None:
        cursor = await self._conn.execute(
            STMT_SAVE_ACCOUNT,
            {
                "account_id": account.id,
                "projects_count": account.projects_count,
                "projects_limit": account.projects_limit,
                "version": get_version(account),
            },
        )
        if cursor.rowcount == 0:
            raise OptimisticLockError


class PostgresProjectRepository(ProjectsRepository):
    def __init__(self, connection: AsyncConnection):
        self._conn = connection

    async def find(self, project_id: str) -> Project | None:
        cursor = await self._conn.execute(STMT_GET_PROJECT, {"project_id": project_id})
        if (row := cursor.one_or_none()) is None:
            return None
        else:
            project = Project(
                id=project_id,
                account_id=row[0],
                name=row[1],
                revision=row[2],
                content=row[3],
                created_at=row[4],
                updated_at=row[5],
                plans_count=row[6],
                plans_limit=row[7],
                published=row[8],
                published_at=row[9],
            )
            set_version(project, int(row[10]))
            return project

    async def save(self, project: Project) -> None:
        cursor = await self._conn.execute(
            STMT_SAVE_PROJECT,
            {
                **project.model_dump(),
                "version": get_version(project),
            },
        )
        if cursor.rowcount == 0:
            raise OptimisticLockError

    async def find_without_content(self, project_id: str) -> Project | None:
        cursor = await self._conn.execute(
            STMT_GET_PROJECT_WITHOUT_CONTENT, {"project_id": project_id}
        )
        if (row := cursor.one_or_none()) is None:
            return None
        else:
            project = Project(
                id=project_id,
                account_id=row[0],
                name=row[1],
                revision=row[2],
                created_at=row[3],
                updated_at=row[4],
                plans_count=row[5],
                plans_limit=row[6],
                published=row[7],
                published_at=row[8],
            )
            set_version(project, int(row[9]))
            return project

    async def save_without_content(self, project: Project) -> None:
        cursor = await self._conn.execute(
            STMT_SAVE_PROJECT_WITHOUT_CONTENT,
            {
                **project.model_dump(exclude={"content"}),
                "version": get_version(project),
            },
        )
        if cursor.rowcount == 0:
            raise OptimisticLockError

    async def delete(self, project_id: str) -> None:
        _ = await self._conn.execute(STMT_DELETE_PROJECT, {"project_id": project_id})

    async def owned_by_account(self, account_id: str) -> list[Project]:
        cursor = await self._conn.execute(
            STMT_GET_ALL_PROJECTS_OWNED_BY_ACCOUNT, {"account_id": account_id}
        )
        projects = [
            Project(
                id=row[0],
                account_id=account_id,
                name=row[1],
                revision=row[2],
                created_at=row[3],
                updated_at=row[4],
                plans_count=row[5],
                plans_limit=row[6],
                published=row[7],
                published_at=row[8],
            )
            for row in cursor.all()
        ]
        return projects


class PostgresPlanRepository(PlansRepository):
    def __init__(self, connection: AsyncConnection):
        self._conn = connection

    async def find(self, plan_id: str) -> Plan | None:
        cursor = await self._conn.execute(STMT_GET_PLAN, {"plan_id": plan_id})
        if (row := cursor.one_or_none()) is None:
            return None
        else:
            plan = Plan(
                id=plan_id,
                project_id=row[0],
                name=row[1],
                revision=row[2],
                content=row[3],
                created_at=row[4],
                updated_at=row[5],
            )
            set_version(plan, int(row[6]))
            return plan

    async def save(self, plan: Plan) -> None:
        cursor = await self._conn.execute(
            STMT_SAVE_PLAN,
            {**plan.model_dump(), "version": get_version(plan)},
        )
        if cursor.rowcount == 0:
            raise OptimisticLockError

    async def find_without_content(self, plan_id: str) -> Plan | None:
        cursor = await self._conn.execute(
            STMT_GET_PLAN_WITHOUT_CONTENT, {"plan_id": plan_id}
        )
        if (row := cursor.one_or_none()) is None:
            return None
        else:
            plan = Plan(
                id=row[0],
                project_id=row[1],
                name=row[2],
                revision=row[3],
                created_at=row[4],
                updated_at=row[5],
            )
            set_version(plan, int(row[6]))
            return plan

    async def save_without_content(self, plan: Plan) -> None:
        cursor = await self._conn.execute(
            STMT_SAVE_PLAN_WITHOUT_CONTENT,
            {**plan.model_dump(), "version": get_version(plan)},
        )
        if cursor.rowcount == 0:
            raise OptimisticLockError

    async def delete(self, plan: Plan) -> None:
        cursor = await self._conn.execute(
            STMT_DELETE_PLAN, {"plan_id": plan.id, "version": get_version(plan)}
        )
        if cursor.rowcount == 0:
            raise OptimisticLockError

    async def in_project(self, project_id: str) -> list[Plan]:
        cursor = await self._conn.execute(
            STMT_GET_PLANS_OF_PROJECT, {"project_id": project_id}
        )
        plans = [
            Plan(
                id=row[0],
                project_id=project_id,
                name=row[1],
                revision=row[2],
                created_at=row[3],
                updated_at=row[4],
            )
            for row in cursor.all()
        ]
        return plans


class PostgresUnitOfWork(UnitOfWork):
    def __init__(self, connection: AsyncConnection):
        self._connection = connection
        self.accounts = PostgresAccountRepository(self._connection)
        self.projects = PostgresProjectRepository(self._connection)
        self.plans = PostgresPlanRepository(self._connection)

    async def commit(self) -> None:
        await self._connection.commit()

    async def rollback(self) -> None:
        await self._connection.rollback()


class PostgresUnitOfWorkFactory(UnitOfWorkFactory):
    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    @asynccontextmanager
    async def begin(self):
        async with self._engine.connect() as connection:
            yield PostgresUnitOfWork(connection)
