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
    account_a_id = "022f51f9-98bb-40af-9d30-0b3c03819212"
    account_b_id = "022f51f9-98bb-40af-9d30-0b3c03819213"

    resp = await client.post(
        "/projects",
        headers={"x-account-id": account_a_id},
    )
    assert resp.status_code == status.HTTP_201_CREATED
    project_id = UUID(resp.json()["id"])

    resp = await client.post(
        f"/projects/{project_id.hex}/plans",
        headers={"x-account-id": account_a_id},
    )
    assert resp.status_code == status.HTTP_201_CREATED
    plan = resp.json()
    plan_id = UUID(plan["id"])

    resp = await client.get(
        f"/projects/{project_id.hex}",
        headers={"x-account-id": account_b_id},
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json() == {"detail": "project not found"}

    resp = await client.get(
        f"/plans/{plan_id.hex}",
        headers={"x-account-id": account_b_id},
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json() == {"detail": "plan not found"}

    resp = await client.post(
        f"/projects/{project_id.hex}/publish",
        headers={"x-account-id": account_a_id},
    )
    assert resp.status_code == status.HTTP_200_OK
    project = resp.json()

    resp = await client.get(
        f"/projects/{project_id.hex}",
        headers={"x-account-id": account_b_id},
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == project

    resp = await client.get(
        f"/plans/{plan_id.hex}",
        headers={"x-account-id": account_b_id},
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == plan

    resp = await client.post(
        f"/projects/{project_id.hex}/unpublish",
        headers={"x-account-id": account_a_id},
    )
    assert resp.status_code == status.HTTP_200_OK

    resp = await client.get(
        f"/projects/{project_id.hex}",
        headers={"x-account-id": account_b_id},
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json() == {"detail": "project not found"}

    resp = await client.get(
        f"/plans/{plan_id.hex}",
        headers={"x-account-id": account_b_id},
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json() == {"detail": "plan not found"}
