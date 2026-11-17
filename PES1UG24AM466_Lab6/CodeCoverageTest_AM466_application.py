import pytest
from pet_boarding import boarding_fee, admission_ok, checkout_status


# ---------- boarding_fee ----------

def test_within_included_days():
    assert boarding_fee("dog", 1, False) == 0


def test_unknown_pet_type():
    with pytest.raises(ValueError):
        boarding_fee("hamster", 2, False)


def test_negative_days():
    with pytest.raises(ValueError):
        boarding_fee("cat", -1, False)


def test_dog_extra_days():
    # dog includes 2 days, so 3 extra days at 30 each
    assert boarding_fee("dog", 5, False) == 90


def test_cat_extra_days():
    # cat includes 3 days, so 2 extra days at 20 each
    assert boarding_fee("cat", 5, False) == 40


def test_premium_kennel_adds_a_day():
    # premium dog includes 3 days, so 2 extra days at 30 each
    assert boarding_fee("dog", 5, True) == 60


def test_long_stay_dog_gets_surcharge():
    # 11 extra days: rate 30 + 10 + 5 = 45 per day
    assert boarding_fee("dog", 13, False) == 495


# ---------- admission_ok ----------

def test_admission_ok():
    assert admission_ok(4, 2, False) is True


def test_senior_pet_needs_three_vaccinations():
    assert admission_ok(9, 3, True) is True


def test_puppy_is_refused():
    assert admission_ok(0.5, 5, False) is False


# ---------- checkout_status ----------

def test_checkout_open():
    assert checkout_status(15, False, False) == "open"


def test_checkout_late():
    assert checkout_status(10, False, False) == "late"


def test_checkout_closed():
    assert checkout_status(-1, False, False) == "closed"


def test_checkout_long_stay_cutoff():
    assert checkout_status(30, True, False) == "open"


def test_checkout_weekend_cutoff():
    assert checkout_status(35, False, True) == "open"
