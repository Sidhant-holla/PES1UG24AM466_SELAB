# Lab 5 – Reflection

**Name:** Sidhant Holla **SRN:** PES1UG24AM466

**1. Which issues were the easiest to fix, and which were the hardest? Why?**

The Flake8 issues were the easiest. E501, E711, E722 and W292 each name the exact line and column and the fix is mechanical — wrap a line, change `== None` to `is None`, add a newline. Adding docstrings and renaming `reserveSeat` to `reserve_seat` were the same kind of work: repetitive but with no thinking involved.

The hardest was `eval()`. Deleting it is easy, but the function existed to apply a discount expression, so I had to decide what should replace that capability. Passing arbitrary arithmetic was the whole point of the original design, and the safe version cannot do that. I settled on a `PROMO_RATES` lookup table, which means the caller now passes a promo *code* rather than an expression. That is a deliberate narrowing of what the function can do, and it is the right trade: a booking system should have a fixed set of promotions, not an arithmetic interpreter.

The mutable default argument was the most interesting. Pylint only says "dangerous default value", which does not tell you what actually goes wrong. I wrote a short probe script that reserved seats for three different customers in three separate calls and printed the function's default argument afterwards — it held all three entries. One customer's order history was visibly leaking into the next call. That took the most effort to understand even though the fix is two lines.

**2. Did the static analysis tools report any false positives? If so, describe one example.**

Yes, and the clearest one was caused by `eval` itself. Pylint reported `base_price` on line 41 as an unused variable (W0612), and Flake8 agreed (F841). It was not unused — `eval(promo_expr)` evaluated the string `"base_price * 0.80"`, which reads that exact variable at runtime. Neither tool can see inside a string that is about to be executed, so both were wrong. The warning disappeared on its own once `eval` was removed and the multiplication became ordinary code.

Bandit B311 is a softer case. It flags `random.randint` as unsuitable for cryptography, and a four digit booking PIN is not cryptography in any strict sense. I still switched to `secrets` because the PIN authorises a ticket and the change costs nothing, but I would not call the original a vulnerability.

The more important finding went the other way: the tools **missed** two real problems. `box_office_key = "BOX_OFFICE_SECRET_PASS_2026"` is a hardcoded secret that the program then prints to stdout, and Bandit's B105 check never fired because it only matches variable names containing words like `password`, `secret` or `token` — `box_office_key` does not. Nothing flagged `main()` being called at module level either, which means importing the file runs the demo and books seats as a side effect. I only noticed that when my probe script printed the demo output before its own.

**3. How would you integrate static analysis tools into your actual software development workflow?**

- Run Flake8 and Pylint in the editor so problems appear while typing rather than at commit time.
- Add a `pre-commit` hook running `flake8`, `pylint --fail-under=9.5` and `bandit -r .` so code that fails cannot be committed in the first place.
- Add a GitHub Actions job running the same three tools on every push and pull request, failing the build on any Bandit Medium or High finding.
- Keep the configuration in the repo (`.pylintrc`, `.flake8`, `pyproject.toml`) so everyone is checked against the same rules rather than whatever their editor defaults to.
- Treat `# nosec` and `# pylint: disable` as requiring a comment explaining why, so suppressions are a decision rather than a habit.

The caveat I would carry over from this lab is that a clean report is not the same as correct code. All three tools passed the hardcoded secret, and two of them actively misreported `base_price`. Static analysis is a filter, not a substitute for reading the code and running it.

**4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?**

- **Security:** the three genuinely dangerous paths are gone. No shell is invoked, so there is no command injection through the filename. `eval` no longer executes caller-supplied strings — I had confirmed it would run `__import__('os').getcwd()` before the fix. Ticket hashes use SHA-256 instead of collision-broken MD5, and the booking PIN is no longer predictable from previous values. Bandit went from 5 issues to 0.
- **Correctness:** each call to `reserve_seat` now gets its own order history instead of appending to one list shared by the whole program. `cancel_seat` reports whether it worked instead of silently swallowing every error.
- **A visible bug fixed by accident:** the "Seating chart exported to:" line used to print before everything else, because `os.system` wrote straight to the terminal while Python's output was still buffered. Replacing it with `print()` put the line back in the right place.
- **Robustness:** the `if __name__ == "__main__":` guard means importing the module no longer books seats. The export file is opened with a context manager and an explicit UTF-8 encoding, so the handle closes on failure and the output is the same on every platform.
- **Readability:** every function has a docstring, names follow PEP 8, and `check_seat_status` went from a four-line if/else returning literals to a single `return not ...`. Pylint went from 5.37 to 10.00 and Flake8 reports nothing.
