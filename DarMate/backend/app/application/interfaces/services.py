"""Ports des services externes et utilitaires (implémentés par l'infrastructure)."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


class UnitOfWork(ABC):
    @abstractmethod
    def commit(self) -> None: ...
    @abstractmethod
    def rollback(self) -> None: ...


class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, password: str) -> str: ...
    @abstractmethod
    def verify(self, password: str, password_hash: str) -> bool: ...


class TokenService(ABC):
    @abstractmethod
    def create_access_token(self, user_id: int, roles: list[str]) -> str: ...
    @abstractmethod
    def new_opaque_token(self) -> tuple[str, str]: ...
    @abstractmethod
    def hash_token(self, raw: str) -> str: ...


@dataclass
class UploadedFile:
    filename: str
    content_type: str
    data: bytes


class FileStorage(ABC):
    """Stockage de fichiers. `private=True` : jamais servi publiquement."""

    @abstractmethod
    def save(self, folder: str, file: UploadedFile, allowed_mimes: dict[str, str],
             max_bytes: int, private: bool) -> str: ...
    @abstractmethod
    def read(self, path: str) -> bytes: ...
    @abstractmethod
    def delete(self, path: str) -> None: ...


class EmailSender(ABC):
    @abstractmethod
    def send(self, to: str, subject: str, body: str) -> None: ...


class RealtimePublisher(ABC):
    @abstractmethod
    def publish_message(self, user_ids: list[int], payload: dict) -> None: ...
