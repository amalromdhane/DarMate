from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    @abstractmethod
    def get(self, id: int) -> T | None: ...
    @abstractmethod
    def add(self, entity: T) -> T: ...
    @abstractmethod
    def update(self, entity: T) -> T: ...
    @abstractmethod
    def delete(self, id: int) -> None: ...
