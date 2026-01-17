from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.plan
@pytest.mark.integration
async def test_plan_crud(
    client: AsyncClient, project_id: str, shell_id: str, headers: dict[str, str]
):
    resp = await client.post(
        f"/projects/{project_id}/plans?shell_id={shell_id}", headers=headers
    )
    assert resp.status_code == status.HTTP_201_CREATED
    plan: dict[str, Any] = resp.json()
    assert plan["name"] == ""
    plan_id = plan["id"]

    resp = await client.get(f"/plans/{plan_id}", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == plan

    resp = await client.patch(
        f"/plans/{plan_id}",
        headers=headers,
        json={"name": "test name"},
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert resp.text == ""

    resp = await client.get(f"/plans/{plan_id}", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["name"] == "test name"

    resp = await client.delete(f"/plans/{plan_id}", headers=headers)
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert resp.text == ""

    resp = await client.get(f"/plans/{plan_id}", headers=headers)
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json() == {"detail": "Not Found"}


@pytest.mark.asyncio
@pytest.mark.plan
@pytest.mark.integration
async def test_patch_plan(
    client: AsyncClient, project_id: str, shell_id: str, headers: dict[str, str]
):
    resp = await client.post(
        f"/projects/{project_id}/plans?shell_id={shell_id}", headers=headers
    )
    assert resp.status_code == status.HTTP_201_CREATED
    plan: dict[str, Any] = resp.json()
    assert plan["version"] == 0
    assert plan["content"] == {
        "furniture": {},
        "areas": {},
    }
    plan_id: str = plan["id"]

    resp = await client.patch(
        f"/plans/{plan_id}/content",
        json={
            "version": 0,
            "furniture": {
                "06c50fb9-eb23-43b6-a1ed-eaff72c39f5f": {
                    "id": "06c50fb9-eb23-43b6-a1ed-eaff72c39f5f",
                    "x": 0,
                    "y": 0,
                    "z": 0,
                    "yaw": 90,
                }
            },
            "areas": {
                "06c50fb9-eb23-43b6-a1ed-eaff72c39f5f": {
                    "id": "06c50fb9-eb23-43b6-a1ed-eaff72c39f5f",
                    "type": "kitchen",
                    "x": 0,
                    "y": 0,
                    "w": 10,
                    "h": 10,
                }
            },
        },
        headers=headers,
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == 1

    resp = await client.get(f"/plans/{plan_id}", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["version"] == 1
    assert resp.json()["content"] == {
        "furniture": {
            "06c50fb9-eb23-43b6-a1ed-eaff72c39f5f": {
                "id": "06c50fb9-eb23-43b6-a1ed-eaff72c39f5f",
                "x": 0,
                "y": 0,
                "z": 0,
                "yaw": 90,
            }
        },
        "areas": {
            "06c50fb9-eb23-43b6-a1ed-eaff72c39f5f": {
                "id": "06c50fb9-eb23-43b6-a1ed-eaff72c39f5f",
                "type": "kitchen",
                "x": 0,
                "y": 0,
                "w": 10,
                "h": 10,
            }
        },
    }

    resp = await client.patch(
        f"/plans/{plan_id}/content",
        json={
            "version": 1,
            "furniture": {
                "06c50fb9-eb23-43b6-a1ed-eaff72c39f5f": {
                    "id": "06c50fb9-eb23-43b6-a1ed-eaff72c39f5f",
                    "x": 1,
                    "yaw": 180,
                }
            },
            "areas": {
                "06c50fb9-eb23-43b6-a1ed-eaff72c39f5f": {
                    "id": "06c50fb9-eb23-43b6-a1ed-eaff72c39f5f",
                    "type": "bedroom",
                    "w": 11,
                    "h": 14,
                }
            },
        },
        headers=headers,
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == 2

    resp = await client.get(f"/plans/{plan_id}", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["version"] == 2
    assert resp.json()["content"] == {
        "furniture": {
            "06c50fb9-eb23-43b6-a1ed-eaff72c39f5f": {
                "id": "06c50fb9-eb23-43b6-a1ed-eaff72c39f5f",
                "x": 1,
                "y": 0,
                "z": 0,
                "yaw": 180,
            }
        },
        "areas": {
            "06c50fb9-eb23-43b6-a1ed-eaff72c39f5f": {
                "id": "06c50fb9-eb23-43b6-a1ed-eaff72c39f5f",
                "type": "bedroom",
                "x": 0,
                "y": 0,
                "w": 11,
                "h": 14,
            }
        },
    }

    resp = await client.patch(
        f"/plans/{plan_id}/content",
        json={
            "version": 2,
            "furniture": {"06c50fb9-eb23-43b6-a1ed-eaff72c39f5f": None},
            "areas": {"06c50fb9-eb23-43b6-a1ed-eaff72c39f5f": None},
        },
        headers=headers,
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == 3

    resp = await client.get(f"/plans/{plan_id}", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["version"] == 3
    assert resp.json()["content"] == {
        "furniture": {},
        "areas": {},
    }


@pytest.mark.asyncio
@pytest.mark.plan
@pytest.mark.integration
async def test_plans_limit_exceeded(
    client: AsyncClient, project_id: str, shell_id: str, headers: dict[str, str]
):
    last_plan_id: str = ""
    for _ in range(20):
        resp = await client.post(
            f"/projects/{project_id}/plans?shell_id={shell_id}", headers=headers
        )
        assert resp.status_code == status.HTTP_201_CREATED
        last_plan_id = resp.json()["id"]

    resp = await client.post(
        f"/projects/{project_id}/plans?shell_id={shell_id}",
        headers=headers,
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json() == {"detail": "plans limit exceeded"}

    resp = await client.delete(f"/plans/{last_plan_id}", headers=headers)
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert resp.text == ""

    resp = await client.post(
        f"/projects/{project_id}/plans?shell_id={shell_id}", headers=headers
    )
    assert resp.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
@pytest.mark.plan
@pytest.mark.integration
async def test_get_all_plans(
    client: AsyncClient, project_id: str, shell_id: str, headers: dict[str, str]
):
    resp = await client.post(
        f"/projects/{project_id}/plans?shell_id={shell_id}", headers=headers
    )
    assert resp.status_code == status.HTTP_201_CREATED
    plan_1 = resp.json()

    resp = await client.post(
        f"/projects/{project_id}/plans?shell_id={shell_id}", headers=headers
    )
    assert resp.status_code == status.HTTP_201_CREATED
    plan_2 = resp.json()

    del plan_1["content"]
    del plan_1["version"]
    del plan_2["content"]
    del plan_2["version"]

    resp = await client.get(f"/projects/{project_id}/plans", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == [plan_1, plan_2] or resp.json() == [
        plan_2,
        plan_1,
    ]
