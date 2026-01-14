from abc import ABC, abstractmethod
from typing import Any, AsyncContextManager, Callable
from uuid import UUID

from app.core.shell.errors import ShellNotFoundError
from app.core.shell.models import Patch, Quota, Shell


class IQuotaRepository(ABC):
    @abstractmethod
    async def get(self, account_id: UUID) -> Quota | None: ...

    @abstractmethod
    async def save(self, quota: Quota) -> None: ...


class IShellsRepository(ABC):
    @abstractmethod
    async def get(self, shell_id: UUID) -> Shell | None: ...

    @abstractmethod
    async def get_content_owned_by_account(
        self, shell_id: UUID, account_id: UUID
    ) -> Shell | None: ...

    @abstractmethod
    async def save(self, shell: Shell) -> None: ...

    @abstractmethod
    async def save_content(self, shell: Shell) -> None: ...

    @abstractmethod
    async def get_no_content(self, shell_id: UUID) -> Shell | None: ...

    @abstractmethod
    async def save_no_content(self, shell: Shell) -> None: ...

    @abstractmethod
    async def get_all_no_content(self, account_id: UUID) -> list[Shell]: ...

    @abstractmethod
    async def delete(self, shell_id: UUID) -> None: ...


class IShellsUnitOfWork(ABC):
    quota: IQuotaRepository
    shells: IShellsRepository

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, traceback: Any):
        if exc:
            await self.rollback()
        else:
            await self.commit()

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...


class ShellService:
    def __init__(
        self,
        uow_factory: Callable[[], AsyncContextManager[IShellsUnitOfWork]],
        max_shells_per_account: int = 20,
    ):
        self.uow_factory = uow_factory
        self.max_shells_per_account = max_shells_per_account

    async def create_shell(self, account_id: UUID) -> Shell:
        async with self.uow_factory() as uow:
            quota = await uow.quota.get(account_id)
            if quota is None:
                quota = Quota.create(account_id, self.max_shells_per_account)
            quota.increase()
            await uow.quota.save(quota)
            shell = Shell.create(account_id)
            await uow.shells.save(shell)
            return shell

    async def get_shell_by_id(self, account_id: UUID, shell_id: UUID) -> Shell | None:
        async with self.uow_factory() as uow:
            shell = await uow.shells.get(shell_id)
            if shell is None or shell.account_id != account_id:
                return None
            return shell

    async def delete_shell(self, account_id: UUID, shell_id: UUID) -> None:
        async with self.uow_factory() as uow:
            shell = await uow.shells.get_no_content(shell_id)
            if shell is None or shell.account_id != account_id:
                return
            quota = await uow.quota.get(account_id)
            if quota is None:
                raise RuntimeError("quota does not exist, however the shell exists")
            quota.decrease()
            await uow.quota.save(quota)
            await uow.shells.delete(shell_id)

    async def rename_shell(self, account_id: UUID, shell_id: UUID, name: str) -> None:
        async with self.uow_factory() as uow:
            shell = await uow.shells.get_no_content(shell_id)
            if shell is None or shell.account_id != account_id:
                raise ShellNotFoundError
            shell.rename(name)
            await uow.shells.save_no_content(shell)

    async def patch_shell(self, account_id: UUID, shell_id: UUID, patch: Patch) -> int:
        async with self.uow_factory() as uow:
            shell = await uow.shells.get_content_owned_by_account(shell_id, account_id)
            if shell is None:
                raise ShellNotFoundError
            shell.patch(patch)
            await uow.shells.save_content(shell)
            return shell.content.version

    async def get_all_shells(self, account_id: UUID) -> list[Shell]:
        async with self.uow_factory() as uow:
            return await uow.shells.get_all_no_content(account_id)
