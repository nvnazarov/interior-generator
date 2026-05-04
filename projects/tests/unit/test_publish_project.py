from contextlib import asynccontextmanager
from unittest.mock import Mock

import pytest

from app.core.account import Account, AccountsRepository
from app.core.project import ProjectsRepository
from app.core.service import AccessDeniedError, ProjectNotFoundError, Service
from app.core.unit_of_work import UnitOfWork, UnitOfWorkFactory


@pytest.mark.asyncio
@pytest.mark.unit
async def test_publish_project():
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
    projects.find_without_content.return_value = project

    project = await service.publish_project(project.id, account.id)

    projects.find_without_content.assert_called_once_with(project.id)
    projects.save_without_content.assert_called_once_with(project)

    assert project.published
    assert project.published_at is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_publish_not_owned_project():
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
        project = await service.publish_project(project.id, account_b.id)

    projects.find_without_content.assert_called_once_with(project.id)
    projects.save_without_content.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_publish_absent_project():
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

    projects.find_without_content.assert_called_once_with("test-project")
    projects.delete.assert_not_called()
