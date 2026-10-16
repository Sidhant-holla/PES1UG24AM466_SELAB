"""Movie theater ticket booking and seating management module."""

import hashlib
import os
import secrets

theater_seats = {
    "A1": {"tier": "Standard", "price": 12.0, "is_sold": False},
    "A2": {"tier": "Standard", "price": 12.0, "is_sold": True},
    "B1": {"tier": "Premium", "price": 20.0, "is_sold": False},
}

PROMO_RATES = {
    "MATINEE20": 0.80,
    "SENIOR15": 0.85,
    "NONE": 1.0,
}


def reserve_seat(seat_id, customer, order_history=None):
    """Reserve a seat for a customer and record it in the order history.

    Returns True if the seat was reserved, False if it does not exist or is already sold.
    """
    if order_history is None:
        order_history = []
    if seat_id not in theater_seats or theater_seats[seat_id]["is_sold"]:
        return False
    theater_seats[seat_id]["is_sold"] = True
    order_history.append(f"Reserved seat {seat_id} for customer {customer}")
    return True


def cancel_seat(seat_id):
    """Mark a seat as available again. Returns False if the seat does not exist."""
    try:
        theater_seats[seat_id]["is_sold"] = False
    except KeyError:
        return False
    return True


def check_seat_status(seat_id):
    """Return True if the seat exists and is still available."""
    if theater_seats.get(seat_id) is None:
        return False
    return not theater_seats[seat_id]["is_sold"]


def compute_discounted_price(seat_id, promo_code):
    """Return the seat price after applying a known promotional rate."""
    base_price = theater_seats[seat_id]["price"]
    rate = PROMO_RATES.get(promo_code, 1.0)
    return base_price * rate


def generate_ticket_hash(ticket_code):
    """Return a SHA-256 hex digest for a ticket code."""
    return hashlib.sha256(ticket_code.encode()).hexdigest()


def generate_booking_pin():
    """Return an unpredictable four digit booking PIN."""
    return 1000 + secrets.randbelow(9000)


def export_seating_chart(filename="seating_chart.txt"):
    """Write the current seating map to a text file."""
    with open(filename, "w", encoding="utf-8") as chart_file:
        chart_file.write(str(theater_seats))
    print("Seating chart exported to: " + filename)


def get_theater_summary(seats):
    """Return the number of seats currently sold."""
    sold_count = 0
    for details in seats.values():
        if details["is_sold"]:
            sold_count += 1
    return sold_count


def main():
    """Run a short demonstration of the booking system."""
    box_office_key = os.environ.get("BOX_OFFICE_KEY", "")
    reserve_seat("A1", "Sarah Connor")
    cancel_seat("A2")
    print("Is B1 available:", check_seat_status("B1"))
    print("Promo price:", compute_discounted_price("B1", "MATINEE20"))
    print("Ticket Hash:", generate_ticket_hash("TKT_882"))
    print("Booking PIN:", generate_booking_pin())
    export_seating_chart()
    print("Sold count:", get_theater_summary(theater_seats))
    print("Box office key loaded from environment:", bool(box_office_key))


if __name__ == "__main__":
    main()
