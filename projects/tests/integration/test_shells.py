from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.shell
@pytest.mark.integration
async def test_shell_crud(client: AsyncClient):
    headers = {"x-account-id": "022f51f9-98bb-40af-9d30-0b3c03819212"}

    resp = await client.post("/shells", headers=headers)
    assert resp.status_code == status.HTTP_201_CREATED
    created_shell: dict[str, Any] = resp.json()
    assert created_shell["name"] == ""
    created_shell_id = created_shell["id"]

    resp = await client.get(f"/shells/{created_shell_id}", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == created_shell

    resp = await client.patch(
        f"/shells/{created_shell_id}",
        headers=headers,
        json={"name": "test name"},
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert resp.text == ""

    resp = await client.get(f"/shells/{created_shell_id}", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["name"] == "test name"

    resp = await client.delete(f"/shells/{created_shell_id}", headers=headers)
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert resp.text == ""

    resp = await client.get(f"/shells/{created_shell_id}", headers=headers)
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json() == {"detail": "Not Found"}


@pytest.mark.asyncio
@pytest.mark.shell
@pytest.mark.integration
async def test_patch_shell(client: AsyncClient):
    headers = {"x-account-id": "022f51f9-98bb-40af-9d30-0b3c03819212"}

    resp = await client.post("/shells", headers=headers)
    assert resp.status_code == status.HTTP_201_CREATED
    created_shell: dict[str, Any] = resp.json()
    assert created_shell["version"] == 0
    assert created_shell["content"] == {
        "walls": {},
        "doors": {},
        "windows": {},
        "wet_areas": {},
    }
    created_shell_id = created_shell["id"]

    resp = await client.patch(
        f"/shells/{created_shell_id}/content",
        headers=headers,
        json={
            "version": 1,
            "walls": {},
        },
    )
    assert resp.status_code == status.HTTP_409_CONFLICT
    assert resp.json() == {"detail": "version conflict"}

    resp = await client.get(f"/shells/{created_shell_id}", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == created_shell

    resp = await client.patch(
        f"/shells/{created_shell_id}/content",
        headers=headers,
        json={
            "version": 0,
            "walls": {
                "dc827c5a-633c-43c1-8816-8ff64eaaeb43": {
                    "id": "dc827c5a-633c-43c1-8816-8ff64eaaeb43",
                    "x1": 0,
                    "y1": 0,
                    "x2": 10,
                    "y2": 0,
                },
            },
            "windows": {
                "af877d39-56e5-4332-b997-dd1a9da3b836": {
                    "id": "af877d39-56e5-4332-b997-dd1a9da3b836",
                    "wall_id": "dc827c5a-633c-43c1-8816-8ff64eaaeb43",
                    "x": 2,
                    "y": 2,
                    "w": 4,
                    "h": 4,
                },
            },
            "doors": {
                "27242d2f-9d7c-4a75-ae15-c462c76f399e": {
                    "id": "27242d2f-9d7c-4a75-ae15-c462c76f399e",
                    "wall_id": "dc827c5a-633c-43c1-8816-8ff64eaaeb43",
                    "x": 7,
                    "w": 2,
                    "h": 4,
                }
            },
            "wet_areas": {
                "7e0360d3-1a66-4521-a8a7-d89dcb6309cf": {
                    "id": "7e0360d3-1a66-4521-a8a7-d89dcb6309cf",
                    "x": 0,
                    "y": 0,
                    "w": 4,
                    "h": 4,
                }
            },
        },
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == 1

    resp = await client.get(f"/shells/{created_shell_id}", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["version"] == 1
    assert resp.json()["content"] == {
        "walls": {
            "dc827c5a-633c-43c1-8816-8ff64eaaeb43": {
                "id": "dc827c5a-633c-43c1-8816-8ff64eaaeb43",
                "x1": 0,
                "y1": 0,
                "x2": 10,
                "y2": 0,
            },
        },
        "windows": {
            "af877d39-56e5-4332-b997-dd1a9da3b836": {
                "id": "af877d39-56e5-4332-b997-dd1a9da3b836",
                "wall_id": "dc827c5a-633c-43c1-8816-8ff64eaaeb43",
                "x": 2,
                "y": 2,
                "w": 4,
                "h": 4,
            },
        },
        "doors": {
            "27242d2f-9d7c-4a75-ae15-c462c76f399e": {
                "id": "27242d2f-9d7c-4a75-ae15-c462c76f399e",
                "wall_id": "dc827c5a-633c-43c1-8816-8ff64eaaeb43",
                "x": 7,
                "w": 2,
                "h": 4,
            }
        },
        "wet_areas": {
            "7e0360d3-1a66-4521-a8a7-d89dcb6309cf": {
                "id": "7e0360d3-1a66-4521-a8a7-d89dcb6309cf",
                "x": 0,
                "y": 0,
                "w": 4,
                "h": 4,
            }
        },
    }

    resp = await client.patch(
        f"/shells/{created_shell_id}/content",
        headers=headers,
        json={
            "version": 1,
            "windows": {
                "af877d39-56e5-4332-b997-dd1a9da3b836": {
                    "w": 9,
                },
            },
        },
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json() == {"detail": "failed to apply the patch"}

    resp = await client.patch(
        f"/shells/{created_shell_id}/content",
        headers=headers,
        json={
            "version": 1,
            "windows": {
                "af877d39-56e5-4332-b997-dd1a9da3b836": {
                    "x": 2,
                    "y": 1,
                    "w": 3,
                    "h": 4,
                },
            },
            "doors": {
                "27242d2f-9d7c-4a75-ae15-c462c76f399e": {
                    "x": 5,
                    "w": 2,
                    "h": 7,
                }
            },
            "wet_areas": {
                "7e0360d3-1a66-4521-a8a7-d89dcb6309cf": None,
            },
        },
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == 2

    resp = await client.get(f"/shells/{created_shell_id}", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["version"] == 2
    assert resp.json()["content"] == {
        "walls": {
            "dc827c5a-633c-43c1-8816-8ff64eaaeb43": {
                "id": "dc827c5a-633c-43c1-8816-8ff64eaaeb43",
                "x1": 0,
                "y1": 0,
                "x2": 10,
                "y2": 0,
            },
        },
        "windows": {
            "af877d39-56e5-4332-b997-dd1a9da3b836": {
                "id": "af877d39-56e5-4332-b997-dd1a9da3b836",
                "wall_id": "dc827c5a-633c-43c1-8816-8ff64eaaeb43",
                "x": 2,
                "y": 1,
                "w": 3,
                "h": 4,
            },
        },
        "doors": {
            "27242d2f-9d7c-4a75-ae15-c462c76f399e": {
                "id": "27242d2f-9d7c-4a75-ae15-c462c76f399e",
                "wall_id": "dc827c5a-633c-43c1-8816-8ff64eaaeb43",
                "x": 5,
                "w": 2,
                "h": 7,
            }
        },
        "wet_areas": {},
    }


@pytest.mark.asyncio
@pytest.mark.project
@pytest.mark.integration
async def test_shells_limit_exceeded(client: AsyncClient):
    headers = {"x-account-id": "022f51f9-98bb-40af-9d30-0b3c03819212"}

    last_shell_id: str = ""
    for _ in range(20):
        resp = await client.post("/shells", headers=headers)
        assert resp.status_code == status.HTTP_201_CREATED
        last_shell_id = resp.json()["id"]

    resp = await client.post("/shells", headers=headers)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json() == {"detail": "shells limit exceeded"}

    resp = await client.delete(f"/shells/{last_shell_id}", headers=headers)
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert resp.text == ""

    resp = await client.post("/shells", headers=headers)
    assert resp.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
@pytest.mark.shell
@pytest.mark.integration
async def test_get_all_shells(client: AsyncClient):
    headers = {"x-account-id": "022f51f9-98bb-40af-9d30-0b3c03819212"}

    resp = await client.post("/shells", headers=headers)
    assert resp.status_code == status.HTTP_201_CREATED
    shell_1 = resp.json()

    resp = await client.post("/shells", headers=headers)
    assert resp.status_code == status.HTTP_201_CREATED
    shell_2 = resp.json()

    del shell_1["version"]
    del shell_1["content"]
    del shell_2["version"]
    del shell_2["content"]

    resp = await client.get("/shells", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == [shell_1, shell_2] or resp.json() == [
        shell_2,
        shell_1,
    ]
