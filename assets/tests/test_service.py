from unittest.mock import Mock

import pytest

from app.core.service import AvatarSizeTooBigError, Service
from app.core.storage import Storage


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_avatar_new():
    storage = Mock(Storage)
    service = Service(storage)
    avatar = bytes(512)
    storage.avatar_exists.return_value = False

    avatar_id = await service.create_avatar(avatar)

    storage.avatar_exists.assert_called_once_with(avatar_id)
    storage.save_avatar.assert_called_once_with(avatar_id, avatar)

    avatar_copy_id = await service.create_avatar(avatar)
    assert avatar_copy_id == avatar_id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_avatar_existed():
    storage = Mock(Storage)
    service = Service(storage)
    avatar = bytes(512)
    storage.avatar_exists.return_value = True

    avatar_id = await service.create_avatar(avatar)

    storage.avatar_exists.assert_called_once_with(avatar_id)
    storage.save_avatar.assert_not_called()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_avatar_too_big():
    storage = Mock(Storage)
    service = Service(storage)

    avatar = bytes(512 * 1024 + 1)
    storage.avatar_exists.return_value = True

    with pytest.raises(AvatarSizeTooBigError):
        _ = await service.create_avatar(avatar)

    storage.avatar_exists.assert_not_called()
    storage.save_avatar.assert_not_called()
