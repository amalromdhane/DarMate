from decimal import Decimal

import pytest

from app.core.exceptions import ConflictError, ValidationFailedError
from app.domain.entities.entities import Property, RoommateProfile
from app.domain.entities.enums import RentalStatus
from app.domain.services.compatibility import CompatibilityWeights, compatibility_score
from app.domain.services.password_policy import validate_password
from app.domain.services.rental_rules import ensure_transition, matches_filters


def profile(**kw):
    base = dict(user_id=1, city_id=1, budget_min=Decimal(300), budget_max=Decimal(500), smoker=False,
                has_pets=False, schedule="EARLY", cleanliness=4, sociability=3)
    return RoommateProfile(**{**base, **kw})


def test_identical_profiles_score_100():
    assert compatibility_score(profile(), profile(user_id=2)) == 100


def test_different_city_and_smoking_lowers_score():
    s = compatibility_score(profile(), profile(user_id=2, city_id=2, smoker=True))
    assert s < 70


def test_weights_are_configurable():
    only_city = CompatibilityWeights.from_settings({f"compat_weight_{k}": "0" for k in CompatibilityWeights.__dataclass_fields__} | {"compat_weight_city": "10"})
    assert compatibility_score(profile(), profile(user_id=2, smoker=True, schedule="NIGHT"), only_city) == 100
    assert compatibility_score(profile(), profile(user_id=2, city_id=9), only_city) == 0


def test_non_overlapping_budget_is_penalised():
    far = profile(user_id=2, budget_min=Decimal(900), budget_max=Decimal(1200))
    assert compatibility_score(profile(), far) < compatibility_score(profile(), profile(user_id=2))


@pytest.mark.parametrize("pw", ["short1A", "alllowercase1", "ALLUPPERCASE1", "NoDigitsHere"])
def test_password_policy_rejects(pw):
    with pytest.raises(ValidationFailedError):
        validate_password(pw)


def test_password_policy_accepts():
    validate_password("GoodPassw0rd")


def test_rental_transitions():
    ensure_transition(RentalStatus.PENDING, RentalStatus.ACCEPTED, as_owner=True)
    ensure_transition(RentalStatus.PENDING, RentalStatus.CANCELLED, as_owner=False)
    with pytest.raises(ConflictError):
        ensure_transition(RentalStatus.REJECTED, RentalStatus.ACCEPTED, as_owner=True)
    with pytest.raises(ConflictError):
        ensure_transition(RentalStatus.PENDING, RentalStatus.ACCEPTED, as_owner=False)


def test_saved_search_matching():
    p = Property(owner_id=1, city_id=3, category_id=1, title="x", price=Decimal("400"), rooms=2, coliving_allowed=True)
    assert matches_filters({"city_id": 3, "max_price": 500}, p)
    assert not matches_filters({"max_price": 300}, p)
    assert not matches_filters({"city_id": 4}, p)
