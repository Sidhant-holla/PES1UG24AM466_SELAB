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


def test_zero_days_is_allowed_and_free():
    # days < 0 is the only invalid case, so 0 must not raise
    assert boarding_fee("cat", 0, False) == 0


def test_exactly_the_included_days_is_free():
    # extra == 0 sits on the boundary of "extra <= 0"
    assert boarding_fee("cat", 3, False) == 0
    assert boarding_fee("rabbit", 4, False) == 0


def test_dog_extra_days():
    # dog includes 2 days, so 3 extra days at 30 each
    assert boarding_fee("dog", 5, False) == 90


def test_cat_extra_days():
    # cat includes 3 days, so 2 extra days at 20 each
    assert boarding_fee("cat", 5, False) == 40


def test_rabbit_extra_days():
    # rabbit includes 4 days, so 2 extra days at 20 each
    assert boarding_fee("rabbit", 6, False) == 40


def test_premium_dog_gets_an_extra_included_day():
    # premium dog includes 3 days, so 2 extra days at 30 each
    assert boarding_fee("dog", 5, True) == 60


def test_premium_cat_gets_an_extra_included_day():
    # premium cat includes 4 days, so 1 extra day at 20
    assert boarding_fee("cat", 5, True) == 20


def test_premium_does_not_help_rabbits():
    # rabbit stays at 4 included days, so 2 extra days at 20 each
    assert boarding_fee("rabbit", 6, True) == 40


def test_premium_dog_exactly_at_its_included_days():
    assert boarding_fee("dog", 3, True) == 0


def test_ten_extra_days_has_no_surcharge():
    # the surcharge starts above 10, so exactly 10 is still the base rate
    assert boarding_fee("dog", 12, False) == 300
    assert boarding_fee("cat", 13, False) == 200


def test_long_stay_dog_gets_surcharge():
    # 11 extra days: rate 30 + 10 + 5 = 45 per day
    assert boarding_fee("dog", 13, False) == 495


def test_long_stay_cat_gets_smaller_surcharge():
    # 11 extra days: rate 20 + 10 = 30 per day, no extra dog surcharge
    assert boarding_fee("cat", 14, False) == 330


def test_long_stay_rabbit_gets_smaller_surcharge():
    assert boarding_fee("rabbit", 15, False) == 330


# ---------- admission_ok ----------

def test_admission_ok():
    assert admission_ok(4, 2, False) is True


def test_senior_pet_needs_three_vaccinations():
    assert admission_ok(9, 3, True) is True
    assert admission_ok(9, 2, True) is False


def test_senior_rule_applies_even_to_a_very_young_flag():
    # is_senior is checked first, so age is ignored
    assert admission_ok(0.2, 3, True) is True


def test_puppy_is_refused_whatever_the_vaccinations():
    assert admission_ok(0.5, 5, False) is False


def test_one_year_old_is_accepted_with_two_vaccinations():
    # age 1 is the boundary of "age < 1"
    assert admission_ok(1, 2, False) is True


def test_adult_with_one_vaccination_is_refused():
    assert admission_ok(5, 1, False) is False


# ---------- checkout_status ----------

def test_checkout_open_on_a_weekday_short_stay():
    assert checkout_status(15, False, False) == "open"


def test_checkout_late_on_a_weekday_short_stay():
    assert checkout_status(14, False, False) == "late"
    assert checkout_status(0, False, False) == "late"


def test_checkout_closed_on_a_weekday_short_stay():
    assert checkout_status(-1, False, False) == "closed"


def test_checkout_long_stay_thresholds():
    assert checkout_status(30, True, False) == "open"
    assert checkout_status(29, True, False) == "late"
    assert checkout_status(15, True, False) == "late"
    assert checkout_status(14, True, False) == "closed"


def test_checkout_weekend_thresholds():
    assert checkout_status(35, False, True) == "open"
    assert checkout_status(34, False, True) == "late"
    assert checkout_status(20, False, True) == "late"
    assert checkout_status(19, False, True) == "closed"


def test_checkout_long_stay_on_a_weekend():
    assert checkout_status(50, True, True) == "open"
    assert checkout_status(49, True, True) == "late"
    assert checkout_status(35, True, True) == "late"
    assert checkout_status(34, True, True) == "closed"
