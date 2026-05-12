from datetime import datetime, timezone

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.plan
@pytest.mark.integration
async def test_create_plan(client: AsyncClient):
    account_id = "test-account"
    resp = await client.post("/projects", headers={"x-account-id": account_id})
    project_id = resp.json()["id"]

    start_time = datetime.now(tz=timezone.utc)
    resp = await client.post(
        f"/projects/{project_id}/plans",
        headers={"x-account-id": account_id},
    )
    finish_time = datetime.now(tz=timezone.utc)

    assert resp.status_code == status.HTTP_201_CREATED
    plan = resp.json()
    assert plan["name"] == ""
    assert plan["content"] == {
        "furniture": {},
        "areas": {},
    }
    assert (
        start_time
        <= datetime.strptime(plan["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(
            tzinfo=timezone.utc
        )
        <= finish_time
    )
    assert resp.json()["updated_at"] == resp.json()["created_at"]
    assert resp.headers.get("etag") is not None


@pytest.mark.asyncio
@pytest.mark.plan
@pytest.mark.integration
async def test_get_plan(client: AsyncClient):
    account_id = "022f51f9-98bb-40af-9d30-0b3c03819212"
    resp = await client.post("/projects", headers={"x-account-id": account_id})
    project_id = resp.json()["id"]
    resp = await client.post(
        f"/projects/{project_id}/plans",
        headers={"x-account-id": account_id},
    )
    plan = resp.json()
    plan_id = plan["id"]
    plan_etag = resp.headers.get("etag")

    resp = await client.get(
        f"/plans/{plan_id}",
        headers={"x-account-id": account_id},
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == plan
    assert resp.headers.get("etag") == plan_etag

    resp = await client.get(
        f"/plans/{plan_id}",
        headers={
            "x-account-id": account_id,
            "if-none-match": plan_etag,
        },
    )
    assert resp.status_code == status.HTTP_304_NOT_MODIFIED
    assert resp.text == ""

    resp = await client.get(
        f"/plans/{plan_id}",
        headers={
            "x-account-id": account_id,
            "if-none-match": "",
        },
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == plan
    assert resp.headers.get("etag") == plan_etag


@pytest.mark.asyncio
@pytest.mark.plan
@pytest.mark.integration
async def test_delete_plan(client: AsyncClient):
    account_id = "022f51f9-98bb-40af-9d30-0b3c03819212"
    other_account_id = "022f51f9-98bb-40af-9d30-0b3c03819213"
    resp = await client.post("/projects", headers={"x-account-id": account_id})
    project_id = resp.json()["id"]
    resp = await client.post(
        f"/projects/{project_id}/plans",
        headers={"x-account-id": account_id},
    )
    plan = resp.json()
    plan_id = plan["id"]

    # Account that does not own the project gets 404 error.
    resp = await client.delete(
        f"/plans/{plan_id}",
        headers={"x-account-id": other_account_id},
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json() == {"detail": "plan not found"}

    resp = await client.delete(
        f"/plans/{plan_id}",
        headers={"x-account-id": account_id},
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert resp.text == ""

    resp = await client.delete(
        f"/plans/{plan_id}",
        headers={"x-account-id": account_id},
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json() == {"detail": "plan not found"}


@pytest.mark.asyncio
@pytest.mark.plan
@pytest.mark.integration
async def test_patch_plan(client: AsyncClient):
    account_id = "022f51f9-98bb-40af-9d30-0b3c03819212"
    resp = await client.post("/projects", headers={"x-account-id": account_id})
    project_id = resp.json()["id"]
    resp = await client.post(
        f"/projects/{project_id}/plans",
        headers={"x-account-id": account_id},
    )
    plan = resp.json()
    plan_id = plan["id"]
    plan_revision = int(plan["revision"])

    # Cannot patch without providing a revision (through If-Match header).
    resp = await client.patch(
        f"/plans/{plan_id}",
        headers={
            "x-account-id": account_id,
        },
        json={},
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # Cannot patch with incorrect revision.
    resp = await client.patch(
        f"/plans/{plan_id}",
        headers={
            "x-account-id": account_id,
            "if-match": str(plan_revision + 1),
        },
        json={},
    )
    assert resp.status_code == status.HTTP_412_PRECONDITION_FAILED
    assert resp.json() == {"detail": "incorrect revision"}

    # Normal patches are applied.
    resp = await client.patch(
        f"/plans/{plan_id}",
        headers={
            "x-account-id": account_id,
            "if-match": str(plan_revision),
        },
        json={
            "name": "test name",
            "content": {
                "furniture": {},
                "areas": {},
            },
        },
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert resp.text == ""


@pytest.mark.asyncio
@pytest.mark.plan
@pytest.mark.integration
async def test_get_plans_of_project(client: AsyncClient):
    account_id = "022f51f9-98bb-40af-9d30-0b3c03819212"
    resp = await client.post("/projects", headers={"x-account-id": account_id})
    project_id = resp.json()["id"]

    resp = await client.post(
        f"/projects/{project_id}/plans",
        headers={"x-account-id": account_id},
    )
    plan_1 = resp.json()

    resp = await client.post(
        f"/projects/{project_id}/plans",
        headers={"x-account-id": account_id},
    )
    plan_2 = resp.json()

    resp = await client.get(
        f"/projects/{project_id}/plans",
        headers={"x-account-id": account_id},
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()[0]["id"] == plan_1["id"]
    assert resp.json()[1]["id"] == plan_2["id"]


@pytest.mark.asyncio
@pytest.mark.plan
@pytest.mark.integration
async def test_plans_limit_exceeded(client: AsyncClient):
    headers = {"x-account-id": "022f51f9-98bb-40af-9d30-0b3c03819212"}
    resp = await client.post("/projects", headers=headers)
    assert resp.status_code == status.HTTP_201_CREATED
    project_id = resp.json()["id"]

    last_plan_id: str = ""
    for _ in range(20):
        resp = await client.post(
            f"/projects/{project_id}/plans",
            headers=headers,
        )
        assert resp.status_code == status.HTTP_201_CREATED
        last_plan_id = resp.json()["id"]

    resp = await client.post(
        f"/projects/{project_id}/plans",
        headers=headers,
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json() == {"detail": "plans limit exceeded"}

    resp = await client.delete(f"/plans/{last_plan_id}", headers=headers)
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert resp.text == ""

    resp = await client.post(
        f"/projects/{project_id}/plans",
        headers=headers,
    )
    assert resp.status_code == status.HTTP_201_CREATED
