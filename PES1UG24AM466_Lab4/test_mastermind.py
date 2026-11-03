import contextlib
import io
import random
import unittest
from unittest import mock

from game import DIFFICULTIES, GameOver, Mastermind, choose_difficulty
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



class DifficultyTests(unittest.TestCase):
    def test_every_difficulty_is_configured(self):
        self.assertEqual(set(DIFFICULTIES), {"easy", "medium", "hard"})

    def test_difficulties_really_differ(self):
        lengths = {c["length"] for c in DIFFICULTIES.values()}
        symbols = {c["symbols"] for c in DIFFICULTIES.values()}
        turns = {c["turns"] for c in DIFFICULTIES.values()}
        self.assertEqual((len(lengths), len(symbols), len(turns)), (3, 3, 3))

    def test_game_uses_the_chosen_configuration(self):
        for name, cfg in DIFFICULTIES.items():
            game = Mastermind(name)
            self.assertEqual(game.length, cfg["length"], name)
            self.assertEqual(game.symbols, cfg["symbols"], name)
            self.assertEqual(game.turns, cfg["turns"], name)
            self.assertEqual(game.difficulty, name)

    def test_secret_code_fits_the_difficulty(self):
        for name, cfg in DIFFICULTIES.items():
            allowed = {str(n) for n in range(1, cfg["symbols"] + 1)}
            for _ in range(200):
                game = Mastermind(name)
                self.assertEqual(len(game.code), cfg["length"], name)
                self.assertTrue(set(game.code) <= allowed, (name, game.code))

    def test_unknown_difficulty_is_rejected(self):
        with self.assertRaises(ValueError):
            Mastermind("impossible")

    def test_default_difficulty_is_medium(self):
        game = Mastermind()
        self.assertEqual((game.length, game.symbols, game.turns), (4, 6, 10))

    def test_win_is_possible_on_every_difficulty(self):
        for name, cfg in DIFFICULTIES.items():
            game = Mastermind(name)
            exact, partial = game.submit("".join(game.code))
            self.assertEqual((exact, partial), (cfg["length"], 0), name)
            self.assertEqual(game.state, "won", name)

    def test_loss_takes_exactly_the_allowed_number_of_guesses(self):
        for name, cfg in DIFFICULTIES.items():
            code = ["1"] * cfg["length"]
            game = Mastermind(name, code=code)
            wrong = "2" * cfg["length"]
            for i in range(cfg["turns"]):
                self.assertEqual(game.state, "playing", (name, i))
                game.submit(wrong)
            self.assertEqual(game.state, "lost", name)
            self.assertEqual(len(game.history), cfg["turns"], name)

    def test_final_turn_win_on_every_difficulty(self):
        for name, cfg in DIFFICULTIES.items():
            code = ["1"] * cfg["length"]
            game = Mastermind(name, code=code)
            for _ in range(cfg["turns"] - 1):
                game.submit("2" * cfg["length"])
            game.submit("1" * cfg["length"])
            self.assertEqual(game.state, "won", name)

    def test_feedback_in_a_live_game_matches_the_reference(self):
        rng = random.Random(7)
        for name, cfg in DIFFICULTIES.items():
            alphabet = [str(n) for n in range(1, cfg["symbols"] + 1)]
            for _ in range(200):
                code = [rng.choice(alphabet) for _ in range(cfg["length"])]
                guess = [rng.choice(alphabet) for _ in range(cfg["length"])]
                game = Mastermind(name, code=code)
                self.assertEqual(
                    game.submit("".join(guess)),
                    reference_feedback(code, guess),
                    (name, code, guess),
                )

    def test_run_asks_for_the_right_length_on_each_difficulty(self):
        for name, cfg in DIFFICULTIES.items():
            game = Mastermind(name, code=["1"] * cfg["length"])
            text = play_script(game, ["q"])
            self.assertIn(f"enter {cfg['length']} digits", text, name)
            self.assertIn(f"1 to {cfg['symbols']}", text, name)

    def test_easy_rejects_a_four_digit_guess(self):
        game = Mastermind("easy", code=list("123"))
        text = play_script(game, ["1234", "q"])
        self.assertIn("Enter exactly 3 digits", text)
        self.assertEqual(game.history, [])

    def test_symbol_range_differs_between_difficulties(self):
        # '7' is out of range on medium (1-6) but fine on hard (1-8)
        medium = Mastermind("medium", code=list("1111"))
        play_script(medium, ["7777", "q"])
        self.assertEqual(medium.history, [])
        hard = Mastermind("hard", code=list("77777"))
        play_script(hard, ["77777"])
        self.assertEqual(hard.state, "won")


class ChooseDifficultyTests(unittest.TestCase):
    def ask(self, inputs):
        out = io.StringIO()
        with mock.patch("builtins.input", side_effect=inputs):
            with contextlib.redirect_stdout(out):
                return choose_difficulty(), out.getvalue()

    def test_enter_picks_the_default(self):
        self.assertEqual(self.ask([""])[0], "medium")

    def test_each_name_is_accepted(self):
        for name in DIFFICULTIES:
            self.assertEqual(self.ask([name])[0], name)

    def test_case_and_whitespace_are_ignored(self):
        self.assertEqual(self.ask(["  HaRd "])[0], "hard")

    def test_bad_choice_asks_again(self):
        choice, text = self.ask(["nightmare", "7", "easy"])
        self.assertEqual(choice, "easy")
        self.assertIn("Choose one of", text)

    def test_end_of_input_falls_back_to_default(self):
        self.assertEqual(self.ask([EOFError()])[0], "medium")

    def test_menu_lists_every_difficulty(self):
        _, text = self.ask([""])
        for name in DIFFICULTIES:
            self.assertIn(name, text)

if __name__ == "__main__":
    unittest.main()
