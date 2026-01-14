import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.project
@pytest.mark.integration
async def test_project_crud(client: AsyncClient):
    headers = {"x-account-id": "022f51f9-98bb-40af-9d30-0b3c03819212"}

    resp = await client.post("/projects", headers=headers)
    assert resp.status_code == status.HTTP_201_CREATED
    created_project = resp.json()
    assert created_project["name"] == ""
    assert created_project["description"] == ""
    assert created_project["pinned"] is False
    created_project_id = created_project["id"]

    resp = await client.get(f"/projects/{created_project_id}", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == created_project

    resp = await client.post(f"/projects/{created_project_id}/pin", headers=headers)
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert resp.text == ""

    resp = await client.get(f"/projects/{created_project_id}", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["pinned"] is True

    resp = await client.post(f"/projects/{created_project_id}/unpin", headers=headers)
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert resp.text == ""

    resp = await client.get(f"/projects/{created_project_id}", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["pinned"] is False

    resp = await client.patch(
        f"/projects/{created_project_id}",
        headers=headers,
        json={
            "name": "test name",
            "description": "test description",
        },
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert resp.text == ""

    resp = await client.get(f"/projects/{created_project_id}", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["name"] == "test name"
    assert resp.json()["description"] == "test description"

    resp = await client.delete(f"/projects/{created_project_id}", headers=headers)
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert resp.text == ""

    resp = await client.get(f"/projects/{created_project_id}", headers=headers)
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json() == {"detail": "Not Found"}


@pytest.mark.asyncio
@pytest.mark.project
@pytest.mark.integration
async def test_get_all_projects(client: AsyncClient):
    headers = {"x-account-id": "022f51f9-98bb-40af-9d30-0b3c03819212"}

    resp = await client.post("/projects", headers=headers)
    assert resp.status_code == status.HTTP_201_CREATED
    project_1 = resp.json()

    resp = await client.post("/projects", headers=headers)
    assert resp.status_code == status.HTTP_201_CREATED
    project_2 = resp.json()

    resp = await client.get("/projects", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == [project_1, project_2] or resp.json() == [
        project_2,
        project_1,
    ]


@pytest.mark.asyncio
@pytest.mark.project
@pytest.mark.integration
async def test_projects_limit_exceeded(client: AsyncClient):
    headers = {"x-account-id": "022f51f9-98bb-40af-9d30-0b3c03819212"}

    last_project_id: str = ""
    for _ in range(20):
        resp = await client.post("/projects", headers=headers)
        assert resp.status_code == status.HTTP_201_CREATED
        last_project_id = resp.json()["id"]

    resp = await client.post("/projects", headers=headers)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json() == {"detail": "projects limit exceeded"}

    resp = await client.delete(f"/projects/{last_project_id}", headers=headers)
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert resp.text == ""

    resp = await client.post("/projects", headers=headers)
    assert resp.status_code == status.HTTP_201_CREATED
