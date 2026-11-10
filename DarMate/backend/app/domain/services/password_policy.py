import re

from app.core.exceptions import ValidationFailedError


def validate_password(password: str) -> None:
    problems = []
    if len(password) < 8:
        problems.append("au moins 8 caractères")
    if not re.search(r"[a-z]", password):
        problems.append("une minuscule")
    if not re.search(r"[A-Z]", password):
        problems.append("une majuscule")
    if not re.search(r"\d", password):
        problems.append("un chiffre")
    if problems:
        raise ValidationFailedError("Le mot de passe doit contenir " + ", ".join(problems) + ".")
