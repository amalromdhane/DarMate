"""Règles métier des demandes de location et des recherches enregistrées."""
from decimal import Decimal

from app.core.exceptions import ConflictError
from app.domain.entities.enums import RentalStatus

OWNER_TRANSITIONS = {
    RentalStatus.PENDING: {RentalStatus.ACCEPTED, RentalStatus.REJECTED},
    RentalStatus.ACCEPTED: {RentalStatus.REJECTED},
}
APPLICANT_TRANSITIONS = {
    RentalStatus.PENDING: {RentalStatus.CANCELLED},
    RentalStatus.ACCEPTED: {RentalStatus.CANCELLED},
}


def ensure_transition(current: RentalStatus, target: RentalStatus, *, as_owner: bool) -> None:
    table = OWNER_TRANSITIONS if as_owner else APPLICANT_TRANSITIONS
    if target not in table.get(current, set()):
        raise ConflictError(f"Impossible de passer la demande de {current.value} à {target.value}.")


def matches_filters(filters: dict, prop) -> bool:
    """Vérifie si une annonce correspond aux critères d'une recherche enregistrée."""
    if filters.get("city_id") and filters["city_id"] != prop.city_id:
        return False
    if filters.get("category_id") and filters["category_id"] != prop.category_id:
        return False
    if filters.get("min_price") is not None and prop.price < Decimal(str(filters["min_price"])):
        return False
    if filters.get("max_price") is not None and prop.price > Decimal(str(filters["max_price"])):
        return False
    if filters.get("min_rooms") and prop.rooms < filters["min_rooms"]:
        return False
    if filters.get("coliving") and not prop.coliving_allowed:
        return False
    return True
