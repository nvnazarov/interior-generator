# import uuid

# import pytest
# import pytest_asyncio
# from testcontainers.postgres import PostgresContainer
# from pydantic import BaseModel

# from projects.infra.db import SQLAlchemyRepository


# class TestData(BaseModel):
#     repository: SQLAlchemyRepository
#     project_id: uuid.UUID
#     project_user_id: uuid.UUID


# @pytest_asyncio.fixture(scope="function")
# async def testdata():
#     with PostgresContainer("postgres:17.5-alpine") as postgres:
#         url = postgres.get_connection_url(driver="asyncpg")
#         repo = SQLAlchemyRepository(url)
#         project_id = uuid.uuid4()
#         project_user_id = uuid.uuid4()
#         await repo.create_project(project_id, project_user_id)
#         yield TestData(
#             repository=repo,
#             project_id=project_id,
#             project_user_id=project_user_id,
#         )


# @pytest.mark.asyncio
# async def test_create_and_delete_plan(testdata: TestData):
#     pass


# @pytest.mark.asyncio
# async def test_patch_plan(testdata: TestData):
#     pass
