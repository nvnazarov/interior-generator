from contextlib import asynccontextmanager
from unittest.mock import Mock

import pytest

from app.core.account import Account, AccountsRepository, ProjectsLimitExceededError
from app.core.project import ProjectsRepository
from app.core.service import Service
from app.core.unit_of_work import UnitOfWork, UnitOfWorkFactory


@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_project_new_account():
    accounts = Mock(AccountsRepository)
    projects = Mock(ProjectsRepository)
    uow = Mock(UnitOfWork)
    uow_factory = Mock(UnitOfWorkFactory)
    uow.accounts = accounts
    uow.projects = projects
    service = Service(uow_factory, plans_limit=10, projects_limit=10)
    account_id = "test"

    @asynccontextmanager
    async def begin():
        yield uow

    uow_factory.begin.return_value = begin()
    accounts.find.return_value = None

    project = await service.create_project(account_id)

    accounts.find.assert_called_once_with(account_id)
    accounts.save.assert_called_once()
    projects.save.assert_called_once()

    assert project.account_id == account_id
    assert project.name == ""
    assert not project.published
    assert project.published_at is None
    assert project.plans_count == 0
    assert project.plans_limit == 10


@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_project_account_exists():
    accounts = Mock(AccountsRepository)
    projects = Mock(ProjectsRepository)
    uow = Mock(UnitOfWork)
    uow_factory = Mock(UnitOfWorkFactory)
    uow.accounts = accounts
    uow.projects = projects
    service = Service(uow_factory, plans_limit=10, projects_limit=10)
    account_id = "test"
    account = Account(id=account_id, projects_count=5, projects_limit=10)

    @asynccontextmanager
    async def begin():
        yield uow

    uow_factory.begin.return_value = begin()
    accounts.find.return_value = account

    project = await service.create_project(account_id)

    accounts.find.assert_called_once_with(account_id)
    accounts.save.assert_called_once()
    projects.save.assert_called_once()

    assert project.account_id == account_id
    assert project.name == ""
    assert not project.published
    assert project.published_at is None
    assert project.plans_count == 0
    assert project.plans_limit == 10
    assert account.projects_count == 6


@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_project_limit_exceed():
    accounts = Mock(AccountsRepository)
    projects = Mock(ProjectsRepository)
    uow = Mock(UnitOfWork)
    uow_factory = Mock(UnitOfWorkFactory)
    uow.accounts = accounts
    uow.projects = projects
    service = Service(uow_factory, plans_limit=10, projects_limit=10)
    account_id = "test"
    account = Account(id=account_id, projects_count=5, projects_limit=5)

    @asynccontextmanager
    async def begin():
        yield uow

    uow_factory.begin.return_value = begin()
    accounts.find.return_value = account

    with pytest.raises(ProjectsLimitExceededError):
        _ = await service.create_project(account_id)
