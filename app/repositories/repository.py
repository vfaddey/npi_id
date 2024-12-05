from abc import ABC, abstractmethod
from uuid import UUID


class Repository(ABC):
    @abstractmethod
    async def add(self, obj):
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: UUID):
        raise NotImplementedError

    @abstractmethod
    async def delete_by_id(self, _id: UUID):
        raise NotImplementedError

    @abstractmethod
    async def update(self, obj):
        raise NotImplementedError