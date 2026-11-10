"""Implémentations concrètes des ports applicatifs."""
import logging
import mimetypes
import secrets
from pathlib import Path

from sqlalchemy.orm import Session

from app.application.interfaces import services as ports
from app.core import security
from app.core.config import settings
from app.core.exceptions import NotFoundError, ValidationFailedError

logger = logging.getLogger("darmate.mail")

# Signatures (magic bytes) pour ne pas se fier au seul type MIME déclaré.
_MAGIC = {
    "image/jpeg": (b"\xff\xd8\xff",),
    "image/png": (b"\x89PNG\r\n\x1a\n",),
    "image/webp": (b"RIFF",),
    "application/pdf": (b"%PDF-",),
}


class SqlUnitOfWork(ports.UnitOfWork):
    def __init__(self, session: Session) -> None:
        self.s = session

    def commit(self) -> None:
        self.s.commit()

    def rollback(self) -> None:
        self.s.rollback()


class Argon2PasswordHasher(ports.PasswordHasher):
    def hash(self, password): return security.hash_password(password)
    def verify(self, password, password_hash): return security.verify_password(password, password_hash)


class JwtTokenService(ports.TokenService):
    def create_access_token(self, user_id, roles): return security.create_access_token(user_id, roles)
    def new_opaque_token(self): return security.new_opaque_token()
    def hash_token(self, raw): return security.hash_token(raw)


class LocalFileStorage(ports.FileStorage):
    """Stockage disque hors racine web. Les fichiers privés ne sont jamais exposés par URL statique."""

    def __init__(self, base_dir: str | None = None) -> None:
        self.base = Path(base_dir or settings.upload_dir).resolve()

    def save(self, folder, file, allowed_mimes, max_bytes, private):
        if len(file.data) == 0:
            raise ValidationFailedError("Le fichier est vide.")
        if len(file.data) > max_bytes:
            raise ValidationFailedError(f"Fichier trop volumineux (maximum {max_bytes // (1024 * 1024)} Mo).")
        mime = file.content_type
        ext = allowed_mimes.get(mime)
        if ext is None:
            raise ValidationFailedError("Type de fichier non autorisé.")
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in (ext, ".jpeg" if ext == ".jpg" else ext):
            raise ValidationFailedError("L'extension du fichier ne correspond pas à son type.")
        magic = _MAGIC.get(mime)
        if magic and not any(file.data.startswith(m) for m in magic):
            raise ValidationFailedError("Le contenu du fichier ne correspond pas à son type.")
        if mime == "image/webp" and file.data[8:12] != b"WEBP":
            raise ValidationFailedError("Le contenu du fichier ne correspond pas à son type.")
        rel = f"{'private' if private else 'public'}/{folder}/{secrets.token_hex(16)}{ext}"
        target = self.base / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(file.data)
        return rel

    def _resolve(self, path: str) -> Path:
        full = (self.base / path).resolve()
        if self.base not in full.parents:  # anti path-traversal
            raise NotFoundError("Fichier introuvable.")
        return full

    def read(self, path):
        full = self._resolve(path)
        if not full.is_file():
            raise NotFoundError("Fichier introuvable.")
        return full.read_bytes()

    def delete(self, path):
        try:
            self._resolve(path).unlink(missing_ok=True)
        except NotFoundError:
            pass


class ConsoleEmailSender(ports.EmailSender):
    """Envoi simulé : journalise l'e-mail (remplacer par SMTP en production)."""

    def send(self, to, subject, body):
        logger.warning("EMAIL à=%s sujet=%s\n%s", to, subject, body)


def guess_mime(path: str) -> str:
    return mimetypes.guess_type(path)[0] or "application/octet-stream"
