from unittest.mock import Mock

import pytest
from httpx import AsyncClient


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(["format"], [("png",), ("jpg",), ("jpeg",)])
async def test_create_avatar(client: AsyncClient, storage: Mock, format: str):
    storage.avatar_exists.return_value = False
    avatar = bytes(512)

    resp = await client.post(
        "/avatars", files={"file": (f"avatar.{format}", avatar, f"image/{format}")}
    )

    assert resp.status_code == 200
    avatar_id = resp.json()
    storage.avatar_exists.assert_called_once()
    storage.save_avatar.assert_called_once_with(avatar_id, avatar)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_avatar_too_big(client: AsyncClient, storage: Mock):
    storage.avatar_exists.return_value = False
    avatar = bytes(512 * 1024 + 1)

    resp = await client.post(
        "/avatars", files={"file": ("avatar.png", avatar, "image/png")}
    )
    assert resp.status_code == 413
    assert resp.json() == {"detail": "file is too big"}

    storage.avatar_exists.assert_not_called()
    storage.save_avatar.assert_not_called()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_avatar_unsupported_format(client: AsyncClient, storage: Mock):
    storage.avatar_exists.return_value = False
    avatar = bytes(512)

    resp = await client.post(
        "/avatars", files={"file": ("avatar.svg", avatar, "image/svg")}
    )
    assert resp.status_code == 400
    assert resp.json() == {"detail": "only jpeg, jpg, and png avatars are supported"}

    storage.avatar_exists.assert_not_called()
    storage.save_avatar.assert_not_called()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 204
    assert resp.text == ""
