from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from app.core.shell.models import Content, Quota, Shell
from app.core.shell.service import (
    IQuotaRepository,
    IShellsRepository,
    IShellsUnitOfWork,
)


class QuotaRepository(IQuotaRepository):
    _get_stmt = text(
        "SELECT current_shells_count, max_shells_count, version "
        "FROM projects.shells_quota "
        "WHERE account_id = :account_id"
    )
    _save_stmt = text(
        "INSERT INTO projects.shells_quota(account_id, current_shells_count, max_shells_count, version) "
        "VALUES (:account_id, :current_shells_count, :max_shells_count, :version) "
        "ON CONFLICT (account_id) DO UPDATE SET "
        "   max_shells_count = excluded.max_shells_count, "
        "   current_shells_count = excluded.current_shells_count, "
        "   version = excluded.version + 1 "
        "WHERE projects.shells_quota.version = :version"
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
                current_shells_count=row[0],
                max_shells_count=row[1],
                version=row[2],
            )

    async def save(self, quota: Quota) -> None:
        cursor = await self._connection.execute(self._save_stmt, quota.model_dump())
        if cursor.rowcount == 0:
            raise RuntimeError("db error: version conflict")


class ShellsRepository(IShellsRepository):
    _delete_stmt = text(
        "UPDATE projects.shells SET deleted = true WHERE id = :shell_id"
    )
    _get_stmt = text(
        "SELECT account_id, name, version, content, created_at, updated_at "
        "FROM projects.shells WHERE id = :shell_id AND deleted = false"
    )
    _get_content_stmt = text(
        "SELECT account_id, name, version, content, created_at, updated_at "
        "FROM projects.shells WHERE id = :shell_id AND account_id = :account_id AND deleted = false"
    )
    _get_no_content_stmt = text(
        "SELECT account_id, name, created_at, updated_at "
        "FROM projects.shells WHERE id = :shell_id AND deleted = false"
    )
    _save_stmt = text(
        "INSERT INTO projects.shells(id, account_id, name, version, content, updated_at, created_at) "
        "VALUES (:id, :account_id, :name, :version, :content, :updated_at, :created_at) "
        "ON CONFLICT (id) DO UPDATE SET "
        "   account_id = excluded.account_id,"
        "   name = excluded.name,"
        "   version = excluded.version, "
        "   content = excluded.content, "
        "   updated_at = excluded.updated_at, "
        "   created_at = excluded.created_at "
        "WHERE projects.shells.id = :id"
    )
    _save_no_content_stmt = text(
        "UPDATE projects.shells SET "
        "   account_id = :account_id,"
        "   name = :name,"
        "   updated_at = :updated_at, "
        "   created_at = :created_at "
        "WHERE projects.shells.id = :id"
    )
    _save_content_stmt = text(
        "INSERT INTO projects.shells(id, account_id, version, content, updated_at, created_at) "
        "VALUES (:id, :account_id, :version + 1, :content, :updated_at, :created_at) "
        "ON CONFLICT (id) DO UPDATE SET "
        "   version = excluded.version, "
        "   content = excluded.content, "
        "   updated_at = excluded.updated_at, "
        "   created_at = excluded.created_at "
        "WHERE projects.shells.id = :id"
    )
    _get_all_no_content_stmt = text(
        "SELECT id, name, created_at, updated_at "
        "FROM projects.shells WHERE account_id = :account_id AND deleted = false"
    )
    _dummy_content = Content()

    def __init__(self, connection: AsyncConnection):
        self._connection = connection

    async def get(self, shell_id: UUID) -> Shell | None:
        cursor = await self._connection.execute(self._get_stmt, {"shell_id": shell_id})
        if (row := cursor.one_or_none()) is None:
            return None
        else:
            return Shell(
                id=shell_id,
                account_id=row[0],
                name=row[1],
                version=row[2],
                content=Content.model_validate(row[3]),
                created_at=row[4],
                updated_at=row[5],
            )

    async def get_content_owned_by_account(
        self, shell_id: UUID, account_id: UUID
    ) -> Shell | None:
        cursor = await self._connection.execute(
            self._get_content_stmt, {"shell_id": shell_id, "account_id": account_id}
        )
        if (row := cursor.one_or_none()) is None:
            return None
        else:
            return Shell(
                id=shell_id,
                account_id=row[0],
                name=row[1],
                version=row[2],
                content=Content.model_validate(row[3]),
                created_at=row[4],
                updated_at=row[5],
            )

    async def get_no_content(self, shell_id: UUID) -> Shell | None:
        cursor = await self._connection.execute(
            self._get_no_content_stmt, {"shell_id": shell_id}
        )
        if (row := cursor.one_or_none()) is None:
            return None
        else:
            return Shell(
                id=shell_id,
                account_id=row[0],
                name=row[1],
                version=0,
                content=self._dummy_content,
                created_at=row[2],
                updated_at=row[3],
            )

    async def get_all_no_content(self, account_id: UUID) -> list[Shell]:
        cursor = await self._connection.execute(
            self._get_all_no_content_stmt, {"account_id": account_id}
        )
        return list(
            map(
                lambda row: Shell(
                    id=row[0],
                    account_id=account_id,
                    name=row[1],
                    version=0,
                    content=self._dummy_content,
                    created_at=row[2],
                    updated_at=row[3],
                ),
                cursor,
            )
        )

    async def save(self, shell: Shell) -> None:
        await self._connection.execute(
            self._save_stmt,
            {
                **shell.model_dump(exclude=set(["content"])),
                "content": shell.content.model_dump_json(),
            },
        )

    async def save_content(self, shell: Shell) -> None:
        await self._connection.execute(
            self._save_content_stmt,
            {
                **shell.model_dump(exclude=set(["content"])),
                "content": shell.content.model_dump_json(),
            },
        )
        shell.version += 1

    async def save_no_content(self, shell: Shell) -> None:
        await self._connection.execute(
            self._save_no_content_stmt, shell.model_dump(exclude=set(["content"]))
        )

    async def delete(self, shell_id: UUID) -> None:
        await self._connection.execute(self._delete_stmt, {"shell_id": shell_id})


class ShellsUnitOfWork(IShellsUnitOfWork):
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
        self.shells = ShellsRepository(self._connection)
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
