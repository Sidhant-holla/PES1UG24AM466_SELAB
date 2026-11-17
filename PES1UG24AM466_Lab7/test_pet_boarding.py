import math

from hypothesis import given, strategies as st
from pet_boarding import parse_booking, stay_average, payable_fee

# Bad input is allowed to be rejected with a ValueError. Any other kind of
# exception (AttributeError, TypeError, ZeroDivisionError ...) counts as a crash.

# Things a caller might pass that are not text at all.
NOT_TEXT = st.one_of(
    st.none(),
    st.integers(),
    st.floats(),
    st.booleans(),
    st.binary(),
    st.lists(st.integers()),
)


# ---------- the function must never crash ----------

@given(st.text() | st.none())
def test_parse_booking_no_crash(s):
    try:
        parse_booking(s)
    except ValueError:
        pass
    except Exception as e:
        assert False, f"parse_booking crashed with: {e!r}"


@given(st.text() | st.none())
def test_stay_average_no_crash(s):
    try:
        stay_average(s)
    except ValueError:
        pass
    except Exception as e:
        assert False, f"stay_average crashed with: {e!r}"


@given(st.text() | st.none())
def test_payable_fee_no_crash(s):
    try:
        payable_fee(s)
    except ValueError:
        pass
    except Exception as e:
        assert False, f"payable_fee crashed with: {e!r}"


@given(NOT_TEXT)
def test_parse_booking_rejects_non_text_cleanly(value):
    try:
        parse_booking(value)
    except ValueError:
        pass
    except Exception as e:
        assert False, f"parse_booking crashed with: {e!r}"


@given(NOT_TEXT)
def test_stay_average_rejects_non_text_cleanly(value):
    try:
        stay_average(value)
    except ValueError:
        pass
    except Exception as e:
        assert False, f"stay_average crashed with: {e!r}"


@given(NOT_TEXT)
def test_payable_fee_rejects_non_text_cleanly(value):
    try:
        payable_fee(value)
    except ValueError:
        pass
    except Exception as e:
        assert False, f"payable_fee crashed with: {e!r}"


# ---------- when it does accept the input, the answer must make sense ----------

@given(st.builds("{}:{}".format, st.text(), st.floats()))
def test_parse_booking_only_returns_sensible_bookings(text):
    try:
        pet, days = parse_booking(text)
    except ValueError:
        return
    assert pet != "", "accepted a booking with no pet name"
    assert math.isfinite(days), "accepted a number of days that is nan or infinite"
    assert days >= 0, "accepted a negative number of days"


@given(
    st.text().filter(lambda p: ":" not in p and p.strip() != ""),
    st.floats(min_value=0, max_value=1e6, allow_nan=False),
)
def test_parse_booking_valid_input(pet, days):
    assert parse_booking(f"{pet}:{days}") == (pet.strip().title(), days)


@given(st.lists(st.integers(min_value=-50, max_value=50), min_size=1))
def test_stay_average_never_negative(stays):
    text = ",".join(str(n) for n in stays)
    try:
        result = stay_average(text)
    except ValueError:
        return
    assert result >= 0, "a stay length cannot be negative"


@given(st.lists(st.integers(min_value=0, max_value=1000), min_size=1))
def test_stay_average_is_between_the_smallest_and_largest(stays):
    result = stay_average(",".join(str(n) for n in stays))
    assert min(stays) <= result <= max(stays)
    assert result == sum(stays) // len(stays)


@given(st.builds("{}|{}".format, st.floats(), st.floats()))
def test_payable_fee_is_finite_and_never_negative(text):
    try:
        result = payable_fee(text)
    except ValueError:
        return
    assert math.isfinite(result), "fee came out as nan or infinity"
    assert result >= 0


@given(st.floats(), st.floats())
def test_a_discount_never_raises_the_fee(fee, discount):
    try:
        result = payable_fee(f"{fee}|{discount}")
    except ValueError:
        return
    assert fee >= 0 and discount >= 0, "accepted a negative fee or discount"
    assert result <= fee * 1.18


@given(
    st.floats(min_value=0, max_value=1e6, allow_nan=False),
    st.floats(min_value=0, max_value=1e6, allow_nan=False),
)
def test_payable_fee_valid_input(fee, discount):
    assert payable_fee(f"{fee}|{discount}") == max(fee * 1.18 - discount, 0)
