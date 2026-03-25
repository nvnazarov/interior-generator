from datetime import datetime, timezone
from uuid import UUID

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.project
@pytest.mark.integration
async def test_create_project(client: AsyncClient):
    account_id = UUID("022f51f9-98bb-40af-9d30-0b3c03819212")

    start_time = datetime.now(tz=timezone.utc)
    resp = await client.post(
        "/projects",
        headers={
            "x-account-id": account_id.hex,
        },
    )
    finish_time = datetime.now(tz=timezone.utc)
    assert resp.status_code == status.HTTP_201_CREATED
    project = resp.json()
    assert project["name"] == ""
    assert project["description"] == ""
    assert project["content"] == {
        "walls": {},
        "windows": {},
        "doors": {},
        "wet_areas": {},
    }
    assert (
        start_time
        <= datetime.strptime(project["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(
            tzinfo=timezone.utc
        )
        <= finish_time
    )
    assert resp.json()["updated_at"] == resp.json()["created_at"]
    assert resp.headers.get("etag") == f"project-{UUID(resp.json()['id']).hex}-0"


@pytest.mark.asyncio
@pytest.mark.project
@pytest.mark.integration
async def test_get_project(client: AsyncClient):
    account_id = UUID("022f51f9-98bb-40af-9d30-0b3c03819212")
    resp = await client.post(
        "/projects",
        headers={
            "x-account-id": account_id.hex,
        },
    )
    project = resp.json()

    resp = await client.get(
        f"/projects/{project['id']}",
        headers={
            "x-account-id": account_id.hex,
        },
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == project
    assert resp.headers.get("etag") == f"project-{UUID(project['id']).hex}-0"

    resp = await client.get(
        f"/projects/{project['id']}",
        headers={
            "x-account-id": account_id.hex,
            "if-none-match": f"project-{UUID(project['id']).hex}-0",
        },
    )
    assert resp.status_code == status.HTTP_304_NOT_MODIFIED
    assert resp.text == ""

    resp = await client.get(
        f"/projects/{project['id']}",
        headers={
            "x-account-id": account_id.hex,
            "if-none-match": f"project-{UUID(project['id']).hex}-1",
        },
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == project
    assert resp.headers.get("etag") == f"project-{UUID(project['id']).hex}-0"


@pytest.mark.asyncio
@pytest.mark.project
@pytest.mark.integration
async def test_delete_project(client: AsyncClient):
    account_id = UUID("022f51f9-98bb-40af-9d30-0b3c03819212")
    other_account_id = UUID("022f51f9-98bb-40af-9d30-0b3c03819213")
    resp = await client.post(
        "/projects",
        headers={
            "x-account-id": account_id.hex,
        },
    )
    project_id = UUID(resp.json()["id"])

    # Account that does not own the project gets 404 error.
    resp = await client.delete(
        f"/projects/{project_id}", headers={"x-account-id": other_account_id.hex}
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json() == {"detail": "project not found"}

    resp = await client.delete(
        f"/projects/{project_id}", headers={"x-account-id": account_id.hex}
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert resp.text == ""

    resp = await client.delete(
        f"/projects/{project_id}", headers={"x-account-id": account_id.hex}
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json() == {"detail": "project not found"}


@pytest.mark.asyncio
@pytest.mark.project
@pytest.mark.integration
async def test_patch_project(client: AsyncClient):
    account_id = UUID("022f51f9-98bb-40af-9d30-0b3c03819212")

    resp = await client.post("/projects", headers={"x-account-id": account_id.hex})
    project = resp.json()
    project_id = UUID(project["id"])

    # Cannot patch without providing a revision (through If-Match header).
    resp = await client.patch(
        f"/projects/{project_id}",
        headers={
            "x-account-id": account_id.hex,
        },
        json={},
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # Cannot patch with incorrect revision.
    resp = await client.patch(
        f"/projects/{project_id}",
        headers={
            "x-account-id": account_id.hex,
            "if-match": f"project-{project_id.hex}-1",  # server expects 0
        },
        json={},
    )
    assert resp.status_code == status.HTTP_412_PRECONDITION_FAILED
    assert resp.json() == {"detail": "incorrect revision"}

    # Normal patches are applied.
    resp = await client.patch(
        f"/projects/{project_id}",
        headers={
            "x-account-id": account_id.hex,
            "if-match": f"project-{project_id.hex}-0",
        },
        json={
            "name": "test name",
            "content": {
                "walls": {},
                "windows": {},
                "doors": {},
                "wet_areas": {},
            },
        },
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert resp.text == ""
    assert resp.headers.get("etag") == f"project-{project_id.hex}-1"

    resp = await client.get(
        f"/projects/{project_id}",
        headers={"x-account-id": account_id.hex},
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["name"] == "test name"
    assert resp.json()["content"] == {
        "walls": {},
        "windows": {},
        "doors": {},
        "wet_areas": {},
    }
    assert resp.headers.get("etag") == f"project-{project_id.hex}-1"


@pytest.mark.asyncio
@pytest.mark.project
@pytest.mark.integration
async def test_get_projects_owned_by_account(client: AsyncClient):
    resp = await client.post(
        "/projects", headers={"x-account-id": "022f51f9-98bb-40af-9d30-0b3c03819212"}
    )
    project_1 = resp.json()

    resp = await client.post(
        "/projects", headers={"x-account-id": "022f51f9-98bb-40af-9d30-0b3c03819212"}
    )
    project_2 = resp.json()

    resp = await client.get(
        "/projects", headers={"x-account-id": "022f51f9-98bb-40af-9d30-0b3c03819212"}
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == [project_2, project_1]

    await client.patch(
        f"/projects/{project_1['id']}",
        headers={
            "x-account-id": "022f51f9-98bb-40af-9d30-0b3c03819212",
            "if-match": f"project-{project_1['id']}-0",
        },
        json={"name": "new name"},
    )

    resp = await client.get(
        "/projects", headers={"x-account-id": "022f51f9-98bb-40af-9d30-0b3c03819212"}
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()[0]["id"] == project_2["id"]
    assert resp.json()[1]["id"] == project_1["id"]


@pytest.mark.asyncio
@pytest.mark.project
@pytest.mark.integration
async def test_projects_limit_exceeded(client: AsyncClient):
    headers = {"x-account-id": "022f51f9-98bb-40af-9d30-0b3c03819212"}

    last_project_id: str = ""
    for _ in range(20):
        resp = await client.post("/projects", headers=headers)
        last_project_id = resp.json()["id"]

    resp = await client.post("/projects", headers=headers)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json() == {"detail": "projects limit exceeded"}

    resp = await client.delete(f"/projects/{last_project_id}", headers=headers)
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert resp.text == ""

    resp = await client.post("/projects", headers=headers)
    assert resp.status_code == status.HTTP_201_CREATED
