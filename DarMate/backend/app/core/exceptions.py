"""Exceptions métier, indépendantes de tout framework."""


class AppError(Exception):
    status_code = 400
    default_message = "Une erreur est survenue."

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class NotFoundError(AppError):
    status_code = 404
    default_message = "Ressource introuvable."


class UnauthorizedError(AppError):
    status_code = 401
    default_message = "Authentification requise ou invalide."


class ForbiddenError(AppError):
    status_code = 403
    default_message = "Vous n'avez pas le droit d'effectuer cette action."


class ConflictError(AppError):
    status_code = 409
    default_message = "Cette opération entre en conflit avec l'état actuel."


class ValidationFailedError(AppError):
    status_code = 422
    default_message = "Les données fournies sont invalides."


class TooManyAttemptsError(AppError):
    status_code = 429
    default_message = "Trop de tentatives. Réessayez plus tard."
