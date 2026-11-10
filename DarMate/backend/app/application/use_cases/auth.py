from datetime import timedelta

from app.application.dto.dto import Actor, AuthResult, RegisterCmd
from app.application.interfaces.services import EmailSender, PasswordHasher, TokenService, UnitOfWork
from app.application.use_cases.common import AuditService
from app.core.clock import utcnow
from app.core.config import settings
from app.core.exceptions import (
    ConflictError, ForbiddenError, TooManyAttemptsError, UnauthorizedError, ValidationFailedError,
)
from app.domain.entities import entities as e
from app.domain.entities.enums import RoleName, UserStatus
from app.domain.repositories import ports
from app.domain.services.password_policy import validate_password

SELF_ASSIGNABLE_ROLES = {RoleName.SEEKER.value, RoleName.OWNER.value}
_DUMMY_HASH: str | None = None


def clean_roles(roles: list[str]) -> list[str]:
    cleaned = sorted(set(roles) & SELF_ASSIGNABLE_ROLES)
    if not cleaned or set(roles) - SELF_ASSIGNABLE_ROLES:
        raise ValidationFailedError("Choisissez le rôle chercheur et/ou propriétaire.")
    return cleaned


class RegisterUser:
    def __init__(self, users: ports.UserRepository, profiles: ports.UserProfileRepository,
                 hasher: PasswordHasher, audit: AuditService, uow: UnitOfWork) -> None:
        self.users, self.profiles, self.hasher, self.audit, self.uow = users, profiles, hasher, audit, uow

    def execute(self, cmd: RegisterCmd) -> e.User:
        validate_password(cmd.password)
        roles = clean_roles(cmd.roles)
        email = cmd.email.strip().lower()
        if self.users.get_by_email(email):
            raise ConflictError("Un compte existe déjà avec cette adresse e-mail.")
        user = self.users.add(e.User(email=email, password_hash=self.hasher.hash(cmd.password), status=UserStatus.ACTIVE))
        self.profiles.add(e.UserProfile(user_id=user.id, first_name=cmd.first_name.strip(),
                                        last_name=cmd.last_name.strip(), phone=cmd.phone))
        self.users.set_roles(user.id, roles)
        self.audit.log(user.id, "user.register", "user", user.id)
        self.uow.commit()
        return user


class LoginUser:
    def __init__(self, users: ports.UserRepository, tokens: ports.RefreshTokenRepository,
                 hasher: PasswordHasher, token_service: TokenService, audit: AuditService, uow: UnitOfWork) -> None:
        self.users, self.tokens, self.hasher, self.ts, self.audit, self.uow = users, tokens, hasher, token_service, audit, uow

    def execute(self, email: str, password: str) -> AuthResult:
        global _DUMMY_HASH
        user = self.users.get_by_email(email.strip().lower())
        if user is None:  # temps constant : évite l'énumération des comptes
            _DUMMY_HASH = _DUMMY_HASH or self.hasher.hash("dummy-Password-1")
            self.hasher.verify(password, _DUMMY_HASH)
            raise UnauthorizedError("Adresse e-mail ou mot de passe incorrect.")
        now = utcnow()
        if user.locked_until and user.locked_until > now:
            raise TooManyAttemptsError("Compte temporairement verrouillé suite à trop de tentatives. Réessayez plus tard.")
        if not self.hasher.verify(password, user.password_hash):
            user.failed_login_count += 1
            if user.failed_login_count >= settings.max_failed_logins:
                user.locked_until = now + timedelta(minutes=settings.lockout_minutes)
                user.failed_login_count = 0
                self.audit.log(user.id, "user.locked", "user", user.id)
            self.users.update(user)
            self.uow.commit()
            raise UnauthorizedError("Adresse e-mail ou mot de passe incorrect.")
        if user.status == UserStatus.PENDING:
            raise ForbiddenError("Votre compte est en attente de validation.")
        if user.status in (UserStatus.SUSPENDED, UserStatus.BANNED):
            raise ForbiddenError("Votre compte est suspendu. Contactez l'assistance.")
        user.failed_login_count, user.locked_until, user.last_login_at = 0, None, now
        self.users.update(user)
        roles = self.users.get_roles(user.id)
        result = _issue_tokens(user, roles, self.tokens, self.ts)
        self.audit.log(user.id, "user.login", "user", user.id)
        self.uow.commit()
        return result


def _issue_tokens(user: e.User, roles: list[str], tokens: ports.RefreshTokenRepository, ts: TokenService) -> AuthResult:
    raw, hashed = ts.new_opaque_token()
    tokens.add(e.RefreshToken(user_id=user.id, token_hash=hashed,
                              expires_at=utcnow() + timedelta(days=settings.refresh_token_expire_days)))
    return AuthResult(ts.create_access_token(user.id, roles), raw, user, roles)


class RefreshSession:
    """Rotation du refresh token avec détection de réutilisation."""

    def __init__(self, users: ports.UserRepository, tokens: ports.RefreshTokenRepository,
                 token_service: TokenService, uow: UnitOfWork) -> None:
        self.users, self.tokens, self.ts, self.uow = users, tokens, token_service, uow

    def execute(self, raw_token: str | None) -> AuthResult:
        if not raw_token:
            raise UnauthorizedError("Session expirée. Veuillez vous reconnecter.")
        stored = self.tokens.get_by_hash(self.ts.hash_token(raw_token))
        if stored is None:
            raise UnauthorizedError("Session expirée. Veuillez vous reconnecter.")
        if stored.revoked_at is not None:  # réutilisation => vol probable : on révoque tout
            self.tokens.revoke_all_for_user(stored.user_id)
            self.uow.commit()
            raise UnauthorizedError("Session invalide. Veuillez vous reconnecter.")
        user = self.users.get(stored.user_id)
        if stored.expires_at < utcnow() or user is None or not user.is_active:
            raise UnauthorizedError("Session expirée. Veuillez vous reconnecter.")
        stored.revoked_at = utcnow()
        self.tokens.update(stored)
        result = _issue_tokens(user, self.users.get_roles(user.id), self.tokens, self.ts)
        self.uow.commit()
        return result


class LogoutUser:
    def __init__(self, tokens: ports.RefreshTokenRepository, token_service: TokenService, uow: UnitOfWork) -> None:
        self.tokens, self.ts, self.uow = tokens, token_service, uow

    def execute(self, raw_token: str | None) -> None:
        if raw_token:
            stored = self.tokens.get_by_hash(self.ts.hash_token(raw_token))
            if stored and stored.revoked_at is None:
                stored.revoked_at = utcnow()
                self.tokens.update(stored)
                self.uow.commit()


class RequestPasswordReset:
    def __init__(self, users: ports.UserRepository, resets: ports.PasswordResetRepository,
                 token_service: TokenService, mailer: EmailSender, uow: UnitOfWork) -> None:
        self.users, self.resets, self.ts, self.mailer, self.uow = users, resets, token_service, mailer, uow

    def execute(self, email: str) -> None:
        user = self.users.get_by_email(email.strip().lower())
        if user is None or not user.is_active:
            return  # réponse identique : pas d'énumération de comptes
        raw, hashed = self.ts.new_opaque_token()
        self.resets.add(e.PasswordResetToken(user_id=user.id, token_hash=hashed,
                                             expires_at=utcnow() + timedelta(minutes=settings.password_reset_expire_minutes)))
        self.uow.commit()
        link = f"{settings.frontend_url}/auth/reset-password?token={raw}"
        self.mailer.send(user.email, "DarMate : réinitialisation du mot de passe",
                         f"Pour choisir un nouveau mot de passe, ouvrez ce lien (valable {settings.password_reset_expire_minutes} min) :\n{link}")


class ResetPassword:
    def __init__(self, users: ports.UserRepository, resets: ports.PasswordResetRepository,
                 tokens: ports.RefreshTokenRepository, hasher: PasswordHasher, token_service: TokenService,
                 audit: AuditService, uow: UnitOfWork) -> None:
        self.users, self.resets, self.tokens, self.hasher, self.ts, self.audit, self.uow = users, resets, tokens, hasher, token_service, audit, uow

    def execute(self, raw_token: str, new_password: str) -> None:
        validate_password(new_password)
        stored = self.resets.get_by_hash(self.ts.hash_token(raw_token))
        if stored is None or stored.used_at is not None or stored.expires_at < utcnow():
            raise ValidationFailedError("Ce lien de réinitialisation est invalide ou a expiré.")
        user = self.users.get(stored.user_id)
        user.password_hash = self.hasher.hash(new_password)
        user.failed_login_count, user.locked_until = 0, None
        self.users.update(user)
        stored.used_at = utcnow()
        self.resets.update(stored)
        self.tokens.revoke_all_for_user(user.id)
        self.audit.log(user.id, "user.password_reset", "user", user.id)
        self.uow.commit()


class ChangePassword:
    def __init__(self, users: ports.UserRepository, tokens: ports.RefreshTokenRepository,
                 hasher: PasswordHasher, audit: AuditService, uow: UnitOfWork) -> None:
        self.users, self.tokens, self.hasher, self.audit, self.uow = users, tokens, hasher, audit, uow

    def execute(self, actor: Actor, current: str, new: str) -> None:
        validate_password(new)
        user = self.users.get(actor.id)
        if not self.hasher.verify(current, user.password_hash):
            raise ValidationFailedError("Le mot de passe actuel est incorrect.")
        user.password_hash = self.hasher.hash(new)
        self.users.update(user)
        self.tokens.revoke_all_for_user(user.id)
        self.audit.log(user.id, "user.password_change", "user", user.id)
        self.uow.commit()
