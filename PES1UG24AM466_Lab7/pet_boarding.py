import math

TAX_MULTIPLIER = 1.18  # 18% tax added to the fee


def _require_text(value, name):
    """Only strings are accepted. Anything else is rejected with a ValueError."""
    if not isinstance(value, str):
        raise ValueError(f"{name} must be text, not {type(value).__name__}")
    return value


def _to_number(token, label):
    """Turn text into a finite, non-negative float or raise ValueError."""
    try:
        number = float(token)
    except ValueError:
        raise ValueError(f"{label} is not a number: {token!r}") from None
    if not math.isfinite(number):
        raise ValueError(f"{label} must be a finite number: {token!r}")
    if number < 0:
        raise ValueError(f"{label} cannot be negative: {token!r}")
    return abs(number)  # abs() also turns -0.0 into 0.0


def parse_booking(text):
    """Turn 'dog:5' into ('Dog', 5.0). Raises ValueError for anything else."""
    text = _require_text(text, "booking")
    parts = text.split(":")
    if len(parts) != 2:
        raise ValueError("booking must look like pet:days")
    pet = parts[0].strip()
    if not pet:
        raise ValueError("pet name is missing")
    days = _to_number(parts[1], "days")
    return pet.title(), days


def stay_average(days_csv):
    """Average stay length (rounded down) of a comma separated list of days."""
    days_csv = _require_text(days_csv, "stay lengths")
    values = []
    for token in days_csv.split(","):
        token = token.strip()
        if not token:
            raise ValueError("stay lengths must not be empty")
        try:
            value = int(token)
        except ValueError:
            raise ValueError(
                f"stay length is not a whole number: {token!r}") from None
        if value < 0:
            raise ValueError(f"stay length cannot be negative: {token!r}")
        values.append(value)
    return sum(values) // len(values)


def payable_fee(text):
    """Fee plus tax minus the discount, from text like '1500|100'."""
    text = _require_text(text, "fee")
    parts = text.split("|")
    if len(parts) != 2:
        raise ValueError("input must look like fee|discount")
    fee = _to_number(parts[0], "fee")
    discount = _to_number(parts[1], "discount")
    total = fee * TAX_MULTIPLIER - discount
    if not math.isfinite(total):
        raise ValueError("fee is too large")
    return max(total, 0.0)


def main():
    print("==== Running parse_booking ====")
    user_input = input("Enter pet:days (e.g. dog:5): ")
    try:
        print("Pet and Days:", parse_booking(user_input))
    except ValueError as error:
        print("Invalid booking:", error)

    print("\n==== Running stay_average ====")
    user_input = input("Enter stay lengths in days as CSV (e.g. 2,5,7): ")
    try:
        print("Average Stay:", stay_average(user_input))
    except ValueError as error:
        print("Invalid stay lengths:", error)

    print("\n==== Running payable_fee ====")
    user_input = input("Enter fee|discount (e.g. 1500|100): ")
    try:
        print("Payable Fee:", payable_fee(user_input))
    except ValueError as error:
        print("Invalid fee:", error)


if __name__ == "__main__":
    main()
