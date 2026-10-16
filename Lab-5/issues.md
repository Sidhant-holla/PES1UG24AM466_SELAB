# Lab 5 – Issue Table (`ticket_booking_system.py`)

**Name:** Sidhant Holla **SRN:** PES1UG24AM466 **Repo:** `L5_45_ticket_booking_system`

Line numbers refer to the **original** file. Ordered by severity (High → Low).

| # | Issue | Tool / Code | Type | Severity | Line(s) | Description | Fix Approach |
|---|-------|-------------|------|----------|---------|-------------|--------------|
| 1 | Shell command injection | Bandit B605 | Security | High | 58 | `os.system("echo Seating chart exported to: " + filename)` builds a shell command by string concatenation. A filename such as `x.txt; rm -rf ~` would run extra commands. The shell call was also pointless — it only echoed a message. | Replaced the whole call with a plain `print()`. No shell is involved at all, so the injection path is gone rather than just narrowed. |
| 2 | Weak hash algorithm | Bandit B324 | Security | High | 47 | `hashlib.md5()` used to generate ticket hashes. MD5 is collision-broken, so two different ticket codes can be made to produce the same hash. | Switched to `hashlib.sha256()`. |
| 3 | Use of `eval()` | Bandit B307 / Pylint W0123 | Security | Medium | 42 | `eval(promo_expr)` executes whatever string the caller passes. Verified by running `compute_discounted_price("B1", "__import__('os').getcwd()")`, which returned the working directory instead of a price — arbitrary code execution, not arithmetic. | Replaced with a `PROMO_RATES` lookup table. The function now takes a promo *code*, looks up a known rate and multiplies. Unknown codes fall back to 1.0. |
| 4 | Mutable default argument | Pylint W0102 | Bug | High (logic) | 15 | `order_history=[]` is created once at definition time and shared by every call. Verified: after reserving seats for three different customers in separate calls, the default list held all three entries, so one customer's order history leaks into the next caller's. | Default changed to `None`; a fresh list is created inside the function when no history is supplied. |
| 5 | Predictable booking PIN | Bandit B311 | Security | Low | 51 | `random.randint` is a Mersenne Twister, not a CSPRNG. Booking PINs that authorise a ticket should not be guessable from previous values. | Use `secrets.randbelow(9000) + 1000`. |
| 6 | Bare `except` that silently passes | Bandit B110 / Pylint W0702 / Flake8 E722 | Bug | Low | 26–27 | `except: pass` swallows every error, including `KeyboardInterrupt`, and the caller cannot tell whether the cancellation worked. | Catch `KeyError` specifically and return `False`; return `True` on success. |
| 7 | Hardcoded secret printed to stdout | *not flagged by any tool* | Security | High | 70, 79 | `box_office_key = "BOX_OFFICE_SECRET_PASS_2026"` is committed in source and then printed. Bandit's B105 did not catch it because the variable name does not contain `password`/`secret`/`token`. | Read from `os.environ.get("BOX_OFFICE_KEY", "")` and print only whether it is configured, never the value. |
| 8 | Unused variables | Pylint W0612 / Flake8 F841 | Bug | Medium | 31, 41 | `booking_fee` is assigned and never used. `base_price` was reported unused only because Pylint cannot see that `eval` consumes it. | `booking_fee` deleted. `base_price` became genuinely used once `eval` was removed. |
| 9 | Unused import | Pylint W0611 / Flake8 F401 | Convention | Low | 6 | `import math` is never used. | Removed. `random` also removed once `secrets` replaced it. |
| 10 | Non-snake_case function name | Pylint C0103 | Convention | Low | 15 | `reserveSeat` breaks PEP 8 naming. | Renamed to `reserve_seat`. |
| 11 | Missing docstrings | Pylint C0116 | Documentation | Low | 15–69 | No function had a docstring. | Added a docstring to every function. |
| 12 | Comparison to `None` with `==` | Pylint C0121 / Flake8 E711 | Convention | Low | 32 | `theater_seats.get(seat_id) == None` should use identity. | Changed to `is None`. |
| 13 | Redundant if/else returning booleans | Pylint R1703 / R1705 | Refactor | Low | 34–37 | `if not sold: return True else: return False` plus an unnecessary `else` after `return`. | Collapsed to `return not theater_seats[seat_id]["is_sold"]`. |
| 14 | File opened without `with` or encoding | Pylint R1732 / W1514 | Robustness | Low | 55 | `open()` without a context manager leaks the handle if the write raises, and without an explicit encoding the result differs between platforms. | `with open(filename, "w", encoding="utf-8") as chart_file:`. |
| 15 | Shadowed outer name | Pylint W0621 | Convention | Low | 61 | The `theater_seats` parameter shadows the module-level dictionary of the same name. | Renamed the parameter to `seats`. |
| 16 | Unused loop variable | Pylint W0612 | Convention | Low | 63 | `for seat, details in ...items()` never uses `seat`. | Iterate `seats.values()` instead. |
| 17 | `%` string formatting | Pylint C0209 | Convention | Low | 19 | Old-style `%` formatting. | Converted to an f-string. |
| 18 | Line too long | Flake8 E501 | Style | Low | 19 | 82 characters, over the 79 limit. Two further E501s appeared in new docstrings and were wrapped. | Wrapped to stay within 79 characters. |
| 19 | No newline at end of file | Pylint C0304 / Flake8 W292 | Style | Low | 82 | File did not end with a newline. | Added. |
| 20 | `main()` called at import time | *not flagged by any tool* | Robustness | Medium | 82 | `main()` runs on import, so the demo executes and seats get booked just by importing the module. Observed while writing a probe script to test the mutable default bug. | Wrapped in `if __name__ == "__main__":`. |

## Results

| Tool | Before | After |
|------|--------|-------|
| Pylint | **5.37 / 10** (25 messages) | **10.00 / 10** |
| Bandit | **5 issues** (2 High, 1 Medium, 2 Low) | **0 issues** |
| Flake8 | **7 issues** | **0 issues** (empty report) |

### A behaviour change worth noting

In the original, `Seating chart exported to: seating_chart.txt` printed *first*, before any of the other output, even though `export_seating_chart()` is called near the end of `main()`. That was because `os.system` wrote straight to the terminal while Python's own output was still buffered. Replacing the shell call with `print()` fixed the ordering as a side effect — the line now appears where it should.
