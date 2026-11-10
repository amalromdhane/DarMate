"""Score de compatibilité entre deux profils de colocation (logique pure, configurable)."""
from dataclasses import dataclass

from app.domain.entities.entities import RoommateProfile


@dataclass(frozen=True)
class CompatibilityWeights:
    budget: float = 30
    city: float = 25
    smoking: float = 15
    pets: float = 10
    schedule: float = 10
    cleanliness: float = 5
    sociability: float = 5

    @classmethod
    def from_settings(cls, raw: dict[str, str]) -> "CompatibilityWeights":
        defaults = cls()
        values = {}
        for name in defaults.__dataclass_fields__:
            try:
                values[name] = float(raw.get(f"compat_weight_{name}", getattr(defaults, name)))
            except ValueError:
                values[name] = getattr(defaults, name)
        return cls(**values)


def _budget_overlap(a: RoommateProfile, b: RoommateProfile) -> float:
    if None in (a.budget_min, a.budget_max, b.budget_min, b.budget_max):
        return 0.5
    low, high = max(a.budget_min, b.budget_min), min(a.budget_max, b.budget_max)
    if high >= low:
        return 1.0
    gap = float(low - high)
    ref = float(max(a.budget_max, b.budget_max)) or 1.0
    return max(0.0, 1 - gap / ref)


def _scale(x: int, y: int) -> float:
    return 1 - abs(x - y) / 4


def compatibility_score(a: RoommateProfile, b: RoommateProfile,
                        w: CompatibilityWeights | None = None) -> int:
    """Retourne un score 0-100."""
    w = w or CompatibilityWeights()
    parts = {
        "budget": _budget_overlap(a, b),
        "city": 1.0 if a.city_id and a.city_id == b.city_id else 0.0,
        "smoking": 1.0 if a.smoker == b.smoker else 0.0,
        "pets": 1.0 if a.has_pets == b.has_pets else 0.5,
        "schedule": 1.0 if a.schedule == b.schedule else (0.6 if "FLEXIBLE" in (a.schedule, b.schedule) else 0.0),
        "cleanliness": _scale(a.cleanliness, b.cleanliness),
        "sociability": _scale(a.sociability, b.sociability),
    }
    total = sum(getattr(w, k) for k in parts)
    if total <= 0:
        return 0
    return round(100 * sum(getattr(w, k) * v for k, v in parts.items()) / total)
