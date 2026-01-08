# from typing import Any
# from uuid import UUID
# from unittest.mock import Mock

# import pytest
# from projects.core.service import ProjectService, IProjectUnitOfWork
# from projects.core.errors import ProjectsPerAccountLimitExceededError


# @pytest.mark.asyncio
# async def test_create_project_limit_exceeded():
#     uow = Mock(IProjectUnitOfWork)

#     async def mock_aenter(*args: Any, **kwargs: Any) -> IProjectUnitOfWork:
#         return uow

#     async def mock_aexit(*args: Any, **kwargs: Any):
#         return

#     uow.get_total_projects_count.return_value = 20
#     uow.__aenter__ = mock_aenter
#     uow.__aexit__ = mock_aexit
#     service = ProjectService(uow, max_projects_per_account=20)
#     with pytest.raises(ProjectsPerAccountLimitExceededError):
#         await service.create_project(UUID("8fbb6021-c763-4361-976d-eb21d32f7e58"))
