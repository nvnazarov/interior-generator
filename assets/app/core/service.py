from hashlib import sha256

from app.core.constants import MAX_AVATAR_SIZE_BYTES
from app.core.models import AvatarID
from app.core.storage import Storage


class AvatarSizeTooBigError(Exception): ...


class Service:
    def __init__(self, storage: Storage):
        self.storage = storage

    async def create_avatar(self, data: bytes) -> AvatarID:
        if len(data) > MAX_AVATAR_SIZE_BYTES:
            raise AvatarSizeTooBigError
        avatar_id = sha256(data).hexdigest()
        avatar_exists = await self.storage.avatar_exists(avatar_id)
        if not avatar_exists:
            await self.storage.save_avatar(avatar_id, data)
        return avatar_id
