import random
import unittest

from logic import feedback


def reference_feedback(code, guess):
    """Independent way of computing feedback, used to cross-check logic.py.

    Total matches are the overlap of the two multisets of symbols. The
    partial count is whatever part of that overlap is not exact.
    """
    exact = sum(c == g for c, g in zip(code, guess))
    overlap = sum(min(code.count(s), guess.count(s)) for s in set(code))
    return exact, overlap - exact


class FeedbackTests(unittest.TestCase):
    def check(self, code, guess, expected):
        got = feedback(list(code), list(guess))
        self.assertEqual(got, expected, f"code={code} guess={guess}")

    def test_all_exact(self):
        self.check("1234", "1234", (4, 0))

    def test_no_matches(self):
        self.check("1111", "2222", (0, 0))

    def test_all_partial(self):
        self.check("1234", "4321", (0, 4))

    def test_mixed_exact_and_partial(self):
        self.check("1234", "1243", (2, 2))

    def test_repeated_guess_symbol_only_counts_once(self):
        # the original reported (1, 3) here
        self.check("1234", "1111", (1, 0))

    def test_repeated_code_symbol_already_used_by_exact(self):
        # the original reported (2, 2) here
        self.check("1123", "1111", (2, 0))

    def test_duplicates_on_both_sides(self):
        self.check("1122", "2211", (0, 4))

    def test_exact_is_resolved_before_partial(self):
        # the original reported (1, 3) here
        self.check("1123", "3111", (1, 2))

    def test_extra_guess_copies_are_ignored(self):
        self.check("6666", "6123", (1, 0))

    def test_guess_has_more_copies_than_code(self):
        self.check("1223", "2221", (2, 1))

    def test_other_code_lengths(self):
        self.check("123", "321", (1, 2))
        self.check("12345", "54321", (1, 4))

    def test_matches_reference_for_every_configuration(self):
        rng = random.Random(2026)
        for length, symbols in [(3, 4), (4, 6), (5, 8), (6, 8)]:
            alphabet = [str(n) for n in range(1, symbols + 1)]
            for _ in range(500):
                code = [rng.choice(alphabet) for _ in range(length)]
                guess = [rng.choice(alphabet) for _ in range(length)]
                self.assertEqual(
                    feedback(code, guess),
                    reference_feedback(code, guess),
                    f"code={code} guess={guess}",
                )


if __name__ == "__main__":
    unittest.main()
