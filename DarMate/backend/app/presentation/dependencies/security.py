# from fastapi import Depends, File, Request, UploadFile
# from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
# from sqlalchemy.orm import Session

# from app.application.dto.dto import Actor
# from app.application.interfaces.services import UploadedFile
# from app.core.dependencies import get_db
# from app.core.exceptions import ForbiddenError, UnauthorizedError, ValidationFailedError
# from app.core.security import decode_access_token
# from app.domain.entities.enums import UserStatus
# from app.infrastructure.container import Container
# from app.domain.repositories.ports import UserRepository

# bearer = HTTPBearer(auto_error=False)


# def provide(use_case: type):
#     """Fabrique une dépendance FastAPI qui construit le use case avec ses dépendances (DI)."""
#     def dependency(db: Session = Depends(get_db)):
#         return Container(db).resolve(use_case)
#     return dependency


# def actor_from_token(token: str, db: Session) -> Actor:
#     data = decode_access_token(token)
#     users = Container(db).resolve(UserRepository)
#     user = users.get(int(data["sub"]))
#     if user is None or user.status != UserStatus.ACTIVE:
#         raise UnauthorizedError("Session invalide.")
#     # les rôles sont relus en base : un changement de rôle s'applique immédiatement
#     return Actor(user.id, tuple(users.get_roles(user.id)))


# def get_current_actor(creds: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> Actor:
#     if creds is None:
#         raise UnauthorizedError()
#     return actor_from_token(creds.credentials, db)


# def get_optional_actor(creds: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> Actor | None:
#     if creds is None:
#         return None
#     try:
#         return actor_from_token(creds.credentials, db)
#     except UnauthorizedError:
#         return None


# def require_admin(actor: Actor = Depends(get_current_actor)) -> Actor:
#     if not actor.is_admin:
#         raise ForbiddenError("Réservé aux administrateurs.")
#     return actor


# async def read_upload(file: UploadFile = File(...)) -> UploadedFile:
#     """Lit le fichier par blocs et refuse au-delà de la limite (protège la mémoire)."""
#     limit, data = 12 * 1024 * 1024, bytearray()
#     while chunk := await file.read(64 * 1024):
#         data.extend(chunk)
#         if len(data) > limit:
#             raise ValidationFailedError("Fichier trop volumineux.")
#     return UploadedFile(file.filename or "", (file.content_type or "").lower(), bytes(data))

from fastapi import Depends, File, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.application.dto.dto import Actor
from app.application.interfaces.services import UploadedFile
from app.core.dependencies import get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError, ValidationFailedError
from app.core.security import decode_access_token
from app.domain.entities.enums import UserStatus
from app.domain.repositories.ports import UserRepository
from app.infrastructure.container import Container

bearer = HTTPBearer(auto_error=False)


def provide(use_case: type):
    """Fabrique une dépendance FastAPI qui construit le use case avec ses dépendances (DI)."""
    def dependency(db: Session = Depends(get_db)):
        return Container(db).resolve(use_case)
    return dependency


def actor_from_token(token: str, db: Session) -> Actor:
    data = decode_access_token(token)
    users = Container(db).resolve(UserRepository)
    user = users.get(int(data["sub"]))
    if user is None or user.status != UserStatus.ACTIVE:
        raise UnauthorizedError("Session invalide.")
    # les rôles sont relus en base à chaque requête
    return Actor(user.id, tuple(users.get_roles(user.id)))


def get_current_actor(creds: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> Actor:
    if creds is None:
        raise UnauthorizedError()
    return actor_from_token(creds.credentials, db)


def get_optional_actor(creds: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> Actor | None:
    if creds is None:
        return None
    try:
        return actor_from_token(creds.credentials, db)
    except UnauthorizedError:
        return None


def require_admin(actor: Actor = Depends(get_current_actor)) -> Actor:
    if not actor.is_admin:
        raise ForbiddenError("Réservé aux administrateurs.")
    return actor


def require_roles(*roles: str):
    """Autorise uniquement les comptes ayant l'un des rôles donnés (403 sinon)."""
    def dependency(actor: Actor = Depends(get_current_actor)) -> Actor:
        if not any(r in actor.roles for r in roles):
            raise ForbiddenError("Cette fonctionnalité n'est pas disponible pour votre type de compte.")
        return actor
    return dependency


require_seeker = require_roles("SEEKER")
require_owner = require_roles("OWNER")


async def read_upload(file: UploadFile = File(...)) -> UploadedFile:
    """Lit le fichier par blocs et refuse au-delà de la limite (protège la mémoire)."""
    limit, data = 12 * 1024 * 1024, bytearray()
    while chunk := await file.read(64 * 1024):
        data.extend(chunk)
        if len(data) > limit:
            raise ValidationFailedError("Fichier trop volumineux.")
    return UploadedFile(file.filename or "", (file.content_type or "").lower(), bytes(data))