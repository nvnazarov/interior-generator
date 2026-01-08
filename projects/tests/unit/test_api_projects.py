from datetime import datetime
from uuid import UUID
from unittest.mock import Mock

from fastapi import status
from fastapi.testclient import TestClient

from projects.api import API
from projects.core.service import ProjectService
from projects.core.models import Project
from projects.core.errors import ProjectNotFoundError


def test_no_authorization_causes_401():
    project_service = Mock(ProjectService)
    api = API(project_service, header_with_account_id="x-account-id")
    client = TestClient(api.asgi(), raise_server_exceptions=False)
    routes = [
        ("get", "/projects"),
        ("post", "/projects"),
        ("get", "/projects/9235f472-1a0f-44ce-a88c-cba7eb6d791f"),
        ("post", "/projects/9235f472-1a0f-44ce-a88c-cba7eb6d791f/pin"),
        ("post", "/projects/9235f472-1a0f-44ce-a88c-cba7eb6d791f/unpin"),
        ("patch", "/projects/9235f472-1a0f-44ce-a88c-cba7eb6d791f"),
        ("delete", "/projects/9235f472-1a0f-44ce-a88c-cba7eb6d791f"),
    ]
    for method, url in routes:
        resp = client.request(method, url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json() == {"detail": "Unauthorized"}


def test_create_project_success():
    project_service = Mock(ProjectService)
    project_service.create_project.return_value = Project(
        id=UUID("e3d3d0af-8067-4035-948c-9f201fa86ca6"),
        account_id=UUID("a870c260-d3d9-46f1-bbd3-069e563b59e5"),
        name="",
        description="",
        pinned=False,
        created_at=datetime(year=2026, month=1, day=1),
        updated_at=datetime(year=2026, month=1, day=1),
    )
    api = API(project_service, header_with_account_id="x-account-id")
    client = TestClient(api.asgi(), raise_server_exceptions=False)
    resp = client.post(
        "/projects",
        headers={"x-account-id": "a870c260-d3d9-46f1-bbd3-069e563b59e5"},
    )
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.json() == {
        "id": "e3d3d0af-8067-4035-948c-9f201fa86ca6",
        "name": "",
        "description": "",
        "pinned": False,
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-01-01T00:00:00",
    }


def test_create_project_unexpected_error():
    project_service = Mock(ProjectService)
    project_service.create_project.side_effect = RuntimeError("unexpected error")
    api = API(project_service, header_with_account_id="x-account-id")
    client = TestClient(api.asgi(), raise_server_exceptions=False)
    resp = client.post(
        "/projects",
        headers={"x-account-id": "a870c260-d3d9-46f1-bbd3-069e563b59e5"},
    )
    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert resp.text == "Internal Server Error"


def test_patch_project_success():
    project_service = Mock(ProjectService)
    project_service.patch_project.return_value = None
    api = API(project_service, header_with_account_id="x-account-id")
    client = TestClient(api.asgi(), raise_server_exceptions=False)
    resp = client.patch(
        "/projects/9235f472-1a0f-44ce-a88c-cba7eb6d791f",
        headers={"x-account-id": "a870c260-d3d9-46f1-bbd3-069e563b59e5"},
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert resp.text == ""


def test_patch_project_unexpected_error():
    project_service = Mock(ProjectService)
    project_service.patch_project.side_effect = RuntimeError("unexpected error")
    api = API(project_service, header_with_account_id="x-account-id")
    client = TestClient(api.asgi(), raise_server_exceptions=False)
    resp = client.patch(
        "/projects/9235f472-1a0f-44ce-a88c-cba7eb6d791f",
        headers={"x-account-id": "a870c260-d3d9-46f1-bbd3-069e563b59e5"},
    )
    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert resp.text == "Internal Server Error"


def test_delete_project_success():
    project_service = Mock(ProjectService)
    project_service.delete_project.return_value = None
    api = API(project_service, header_with_account_id="x-account-id")
    client = TestClient(api.asgi(), raise_server_exceptions=False)
    resp = client.delete(
        "/projects/9235f472-1a0f-44ce-a88c-cba7eb6d791f",
        headers={"x-account-id": "a870c260-d3d9-46f1-bbd3-069e563b59e5"},
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert resp.text == ""


def test_delete_project_unexpected_error():
    project_service = Mock(ProjectService)
    project_service.delete_project.side_effect = RuntimeError("unexpected error")
    api = API(project_service, header_with_account_id="x-account-id")
    client = TestClient(api.asgi(), raise_server_exceptions=False)
    resp = client.delete(
        "/projects/9235f472-1a0f-44ce-a88c-cba7eb6d791f",
        headers={"x-account-id": "a870c260-d3d9-46f1-bbd3-069e563b59e5"},
    )
    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert resp.text == "Internal Server Error"


def test_pin_project_success():
    project_service = Mock(ProjectService)
    project_service.pin_project.return_value = None
    api = API(project_service, header_with_account_id="x-account-id")
    client = TestClient(api.asgi(), raise_server_exceptions=False)
    resp = client.post(
        "/projects/9235f472-1a0f-44ce-a88c-cba7eb6d791f/pin",
        headers={"x-account-id": "a870c260-d3d9-46f1-bbd3-069e563b59e5"},
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert resp.text == ""


def test_pin_project_does_not_exist():
    project_service = Mock(ProjectService)
    project_service.pin_project.side_effect = ProjectNotFoundError
    api = API(project_service, header_with_account_id="x-account-id")
    client = TestClient(api.asgi(), raise_server_exceptions=False)
    resp = client.post(
        "/projects/9235f472-1a0f-44ce-a88c-cba7eb6d791f/pin",
        headers={"x-account-id": "a870c260-d3d9-46f1-bbd3-069e563b59e5"},
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json() == {"detail": "Not Found"}


def test_pin_project_unexpected_error():
    project_service = Mock(ProjectService)
    project_service.pin_project.side_effect = RuntimeError("unexpected error")
    api = API(project_service, header_with_account_id="x-account-id")
    client = TestClient(api.asgi(), raise_server_exceptions=False)
    resp = client.post(
        "/projects/9235f472-1a0f-44ce-a88c-cba7eb6d791f/pin",
        headers={"x-account-id": "a870c260-d3d9-46f1-bbd3-069e563b59e5"},
    )
    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert resp.text == "Internal Server Error"


def test_unpin_project_success():
    project_service = Mock(ProjectService)
    project_service.unpin_project.return_value = None
    api = API(project_service, header_with_account_id="x-account-id")
    client = TestClient(api.asgi(), raise_server_exceptions=False)
    resp = client.post(
        "/projects/9235f472-1a0f-44ce-a88c-cba7eb6d791f/unpin",
        headers={"x-account-id": "a870c260-d3d9-46f1-bbd3-069e563b59e5"},
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert resp.text == ""


def test_unpin_project_does_not_exist():
    project_service = Mock(ProjectService)
    project_service.unpin_project.side_effect = ProjectNotFoundError
    api = API(project_service, header_with_account_id="x-account-id")
    client = TestClient(api.asgi(), raise_server_exceptions=False)
    resp = client.post(
        "/projects/9235f472-1a0f-44ce-a88c-cba7eb6d791f/unpin",
        headers={"x-account-id": "a870c260-d3d9-46f1-bbd3-069e563b59e5"},
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json() == {"detail": "Not Found"}


def test_unpin_project_unexpected_error():
    project_service = Mock(ProjectService)
    project_service.unpin_project.side_effect = RuntimeError("unexpected error")
    api = API(project_service, header_with_account_id="x-account-id")
    client = TestClient(api.asgi(), raise_server_exceptions=False)
    resp = client.post(
        "/projects/9235f472-1a0f-44ce-a88c-cba7eb6d791f/unpin",
        headers={"x-account-id": "a870c260-d3d9-46f1-bbd3-069e563b59e5"},
    )
    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert resp.text == "Internal Server Error"
