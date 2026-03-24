from hashlib import sha256

from app.core.models import AvatarID
from app.core.storage import Storage


class Service:
    def __init__(self, storage: Storage):
        self.storage = storage

    async def create_avatar(self, data: bytes) -> AvatarID:
        avatar_id = sha256(data).hexdigest()
        if not (await self.storage.avatar_exists(avatar_id)):
            await self.storage.save_avatar(avatar_id, data)
        return avatar_id
