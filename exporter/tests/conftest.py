# import pytest
# import pytest_asyncio
# from asgi_lifespan import LifespanManager
# from httpx import ASGITransport, AsyncClient

# from app.api.api import API
# from app.core.exporter import Exporter

# @pytest.fixture
# def project():
#     pass


# @pytest.fixture
# def api():
#     exporter = Exporter()
#     api = API(exporter)
#     return api


# @pytest_asyncio.fixture(scope="function")
# async def client(api: API):
#     app = api.asgi()
#     transport = ASGITransport(app)
#     async with LifespanManager(app):
#         async with AsyncClient(transport=transport, base_url="http://test") as client:
#             yield client
