from contextlib import asynccontextmanager
from unittest.mock import Mock

import pytest

from app.core.account import Account, AccountsRepository
from app.core.project import ProjectsRepository
from app.core.service import AccessDeniedError, ProjectNotFoundError, Service
from app.core.unit_of_work import UnitOfWork, UnitOfWorkFactory


@pytest.mark.asyncio
@pytest.mark.unit
async def test_delete_project():
    accounts = Mock(AccountsRepository)
    projects = Mock(ProjectsRepository)
    uow = Mock(UnitOfWork)
    uow_factory = Mock(UnitOfWorkFactory)
    uow.accounts = accounts
    uow.projects = projects
    service = Service(uow_factory, plans_limit=10, projects_limit=10)
    account = Account(id="test-account", projects_limit=10)
    project = account.create_project(plans_limit=10)

    @asynccontextmanager
    async def begin():
        yield uow

    uow_factory.begin.return_value = begin()
    accounts.find.return_value = account
    projects.find.return_value = project

    await service.delete_project(account.id, project.id)

    accounts.find.assert_called_once_with(account.id)
    accounts.save.assert_called_once()
    projects.find_without_content.assert_called_once_with(project.id)
    projects.delete.assert_called_once_with(project.id)

    assert account.projects_count == 0


@pytest.mark.asyncio
@pytest.mark.unit
async def test_delete_not_owned_project():
    accounts = Mock(AccountsRepository)
    projects = Mock(ProjectsRepository)
    uow = Mock(UnitOfWork)
    uow_factory = Mock(UnitOfWorkFactory)
    uow.accounts = accounts
    uow.projects = projects
    service = Service(uow_factory, plans_limit=10, projects_limit=10)
    account_a = Account(id="a", projects_limit=10)
    account_b = Account(id="b", projects_limit=10)
    project = account_a.create_project(plans_limit=10)

    @asynccontextmanager
    async def begin():
        yield uow

    uow_factory.begin.return_value = begin()
    accounts.find.return_value = account_b
    projects.find_without_content.return_value = project

    with pytest.raises(AccessDeniedError):
        _ = await service.delete_project(account_b.id, project.id)

    accounts.find.assert_called_once_with(account_b.id)
    accounts.save.assert_not_called()
    projects.find_without_content.assert_called_once_with(project.id)
    projects.delete.assert_not_called()

    assert account_a.projects_count == 1
    assert account_b.projects_count == 0


@pytest.mark.asyncio
@pytest.mark.unit
async def test_delete_project_new_account():
    accounts = Mock(AccountsRepository)
    projects = Mock(ProjectsRepository)
    uow = Mock(UnitOfWork)
    uow_factory = Mock(UnitOfWorkFactory)
    uow.accounts = accounts
    uow.projects = projects
    service = Service(uow_factory, plans_limit=10, projects_limit=10)
    account_id = "test-account"

    @asynccontextmanager
    async def begin():
        yield uow

    uow_factory.begin.return_value = begin()
    accounts.find.return_value = None

    with pytest.raises(ProjectNotFoundError):
        await service.delete_project(account_id, "test-project")

    accounts.find.assert_called_once_with(account_id)
    projects.find_without_content.assert_not_called()
    projects.delete.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_delete_absent_project():
    accounts = Mock(AccountsRepository)
    projects = Mock(ProjectsRepository)
    uow = Mock(UnitOfWork)
    uow_factory = Mock(UnitOfWorkFactory)
    uow.accounts = accounts
    uow.projects = projects
    service = Service(uow_factory, plans_limit=10, projects_limit=10)
    account = Account(id="test-account", projects_limit=10)

    @asynccontextmanager
    async def begin():
        yield uow

    uow_factory.begin.return_value = begin()
    accounts.find.return_value = account
    projects.find_without_content.return_value = None

    with pytest.raises(ProjectNotFoundError):
        await service.delete_project(account.id, "test-project")

    accounts.find.assert_called_once_with(account.id)
    projects.find_without_content.assert_called_once_with("test-project")
    projects.delete.assert_not_called()
