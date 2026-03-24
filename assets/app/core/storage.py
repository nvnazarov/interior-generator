from abc import ABC, abstractmethod

from app.core.models import AvatarID


class Storage(ABC):
    @abstractmethod
    async def avatar_exists(self, id: AvatarID) -> bool: ...

    @abstractmethod
    async def save_avatar(self, id: AvatarID, data: bytes): ...
