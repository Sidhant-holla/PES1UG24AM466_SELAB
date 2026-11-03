import contextlib
import io
import random
import unittest
from unittest import mock

from game import GameOver, Mastermind
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


WRONG = "6666"          # never matches the fixed code below
CODE = "1234"


def play_script(game, inputs):
    """Run game.run() with scripted keyboard input. Returns what it printed."""
    out = io.StringIO()
    with mock.patch("builtins.input", side_effect=inputs):
        with contextlib.redirect_stdout(out):
            game.run()
    return out.getvalue()


class LifecycleTests(unittest.TestCase):
    def new_game(self):
        return Mastermind(code=CODE)

    def test_new_game_starts_in_playing_state(self):
        game = self.new_game()
        self.assertEqual(game.state, "playing")
        self.assertEqual(game.turns, 10)
        self.assertEqual(game.history, [])

    def test_win_is_recorded(self):
        game = self.new_game()
        self.assertEqual(game.submit("1234"), (4, 0))
        self.assertEqual(game.state, "won")
        self.assertEqual(game.turns, 9)

    def test_win_on_the_final_turn_is_a_win_not_a_loss(self):
        game = self.new_game()
        for _ in range(9):
            game.submit(WRONG)
        self.assertEqual(game.turns, 1)
        self.assertEqual(game.state, "playing")
        game.submit("1234")
        self.assertEqual(game.turns, 0)
        self.assertEqual(game.state, "won")

    def test_loss_after_the_last_wrong_guess(self):
        game = self.new_game()
        for _ in range(10):
            game.submit(WRONG)
        self.assertEqual(game.state, "lost")
        self.assertEqual(game.turns, 0)

    def test_guess_limit_is_enforced(self):
        game = self.new_game()
        for _ in range(10):
            game.submit(WRONG)
        with self.assertRaises(GameOver):
            game.submit(WRONG)
        self.assertEqual(len(game.history), 10)
        self.assertEqual(game.turns, 0)

    def test_nothing_changes_after_a_win(self):
        game = self.new_game()
        game.submit("1234")
        before = (list(game.history), game.turns, game.state)
        with self.assertRaises(GameOver):
            game.submit(WRONG)
        self.assertEqual((list(game.history), game.turns, game.state), before)

    def test_nothing_changes_after_a_loss(self):
        game = self.new_game()
        for _ in range(10):
            game.submit(WRONG)
        before = (list(game.history), game.turns, game.state)
        with self.assertRaises(GameOver):
            game.submit("1234")
        self.assertEqual((list(game.history), game.turns, game.state), before)
        self.assertEqual(game.state, "lost")

    def test_quit_ends_the_game_and_blocks_further_guesses(self):
        game = self.new_game()
        game.submit(WRONG)
        game.quit()
        self.assertEqual(game.state, "quit")
        with self.assertRaises(GameOver):
            game.submit("1234")
        self.assertEqual(len(game.history), 1)

    def test_quit_cannot_overwrite_a_finished_game(self):
        game = self.new_game()
        game.submit("1234")
        game.quit()
        self.assertEqual(game.state, "won")

    def test_history_is_preserved_in_order(self):
        game = self.new_game()
        game.submit("1111")
        game.submit("2341")
        game.submit("1234")
        self.assertEqual(
            game.history,
            [("1111", 1, 0), ("2341", 0, 4), ("1234", 4, 0)],
        )

    def test_run_reports_a_win(self):
        game = self.new_game()
        text = play_script(game, ["6666", "1234"])
        self.assertIn("Cracked the code in 2 guesses", text)
        self.assertEqual(game.state, "won")

    def test_run_reports_a_loss_and_reveals_the_code(self):
        game = self.new_game()
        text = play_script(game, [WRONG] * 10)
        self.assertIn("Out of turns. The code was 1234", text)
        self.assertEqual(game.state, "lost")

    def test_run_quit_with_q(self):
        game = self.new_game()
        text = play_script(game, ["q"])
        self.assertEqual(game.state, "quit")
        self.assertIn("Game ended", text)

    def test_run_quit_on_end_of_input(self):
        game = self.new_game()
        play_script(game, [EOFError()])
        self.assertEqual(game.state, "quit")

    def test_run_does_not_ask_again_after_the_game_ends(self):
        game = self.new_game()
        with mock.patch("builtins.input", side_effect=["1234", "extra"]) as fake:
            with contextlib.redirect_stdout(io.StringIO()):
                game.run()
        self.assertEqual(fake.call_count, 1)
        self.assertEqual(game.state, "won")
        self.assertEqual(len(game.history), 1)


if __name__ == "__main__":
    unittest.main()
