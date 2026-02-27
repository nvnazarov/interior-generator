from typing import Any
from uuid import UUID

import pytest
from fastapi import status
from httpx import AsyncClient


def omit(a: dict[str, Any], k: str) -> dict[str, Any]:
    b = a.copy()
    del b[k]
    return b


@pytest.mark.asyncio
@pytest.mark.project
@pytest.mark.plan
@pytest.mark.integration
async def test_publish_project(client: AsyncClient):
    account_a_id = UUID("022f51f9-98bb-40af-9d30-0b3c03819212")
    account_b_id = UUID("022f51f9-98bb-40af-9d30-0b3c03819213")

    resp = await client.post(
        "/projects",
        headers={"x-account-id": account_a_id.hex},
    )
    assert resp.status_code == status.HTTP_201_CREATED
    project = resp.json()
    project_id = UUID(project["id"])

    resp = await client.post(
        f"/projects/{project_id.hex}/plans",
        headers={"x-account-id": account_a_id.hex},
    )
    assert resp.status_code == status.HTTP_201_CREATED
    plan = resp.json()
    plan_id = UUID(plan["id"])

    resp = await client.get(
        f"/projects/{project_id.hex}",
        headers={"x-account-id": account_b_id.hex},
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json() == {"detail": "project not found"}

    resp = await client.get(
        f"/plans/{plan_id.hex}",
        headers={"x-account-id": account_b_id.hex},
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json() == {"detail": "plan not found"}

    resp = await client.post(
        f"/projects/{project_id.hex}/publish",
        headers={"x-account-id": account_a_id.hex},
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert resp.text == ""
    project["published"] = True

    resp = await client.get(
        f"/projects/{project_id.hex}",
        headers={"x-account-id": account_b_id.hex},
    )
    assert resp.status_code == status.HTTP_200_OK
    assert omit(resp.json(), "updated_at") == omit(project, "updated_at")

    resp = await client.get(
        f"/plans/{plan_id.hex}",
        headers={"x-account-id": account_b_id.hex},
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == plan

    resp = await client.post(
        f"/projects/{project_id.hex}/unpublish",
        headers={"x-account-id": account_a_id.hex},
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert resp.text == ""
    project["published"] = False

    resp = await client.get(
        f"/projects/{project_id.hex}",
        headers={"x-account-id": account_b_id.hex},
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json() == {"detail": "project not found"}

    resp = await client.get(
        f"/plans/{plan_id.hex}",
        headers={"x-account-id": account_b_id.hex},
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json() == {"detail": "plan not found"}
