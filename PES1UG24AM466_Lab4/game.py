import random
from logic import feedback

# Each difficulty changes the length of the code, the range of symbols
# (1..symbols) and the number of guesses the player gets.
DIFFICULTIES = {
    "easy": {"length": 3, "symbols": 4, "turns": 12},
    "medium": {"length": 4, "symbols": 6, "turns": 10},
    "hard": {"length": 5, "symbols": 8, "turns": 8},
}
DEFAULT_DIFFICULTY = "medium"


class GameOver(Exception):
    """Raised when a guess is submitted after the game has already ended."""


def describe(name):
    """One line summary of a difficulty, for the menu."""
    cfg = DIFFICULTIES[name]
    return (f"{name:<7} {cfg['length']} positions, symbols 1-{cfg['symbols']}, "
            f"{cfg['turns']} guesses")


def choose_difficulty():
    """Ask which difficulty to play. Enter picks the default."""
    print("Choose a difficulty:")
    for name in DIFFICULTIES:
        print("  " + describe(name))
    while True:
        try:
            raw = input(f"Difficulty [{DEFAULT_DIFFICULTY}] > ").strip().lower()
        except EOFError:
            return DEFAULT_DIFFICULTY
        if raw == "":
            return DEFAULT_DIFFICULTY
        if raw in DIFFICULTIES:
            return raw
        print("Choose one of:", ", ".join(DIFFICULTIES))


def validate_guess(raw, length, symbols):
    """Return a message explaining what is wrong with a guess, or None."""
    if raw == "":
        return "Enter a guess, or q to quit."
    if len(raw) != length:
        return f"A guess needs exactly {length} digits, you entered {len(raw)}."
    allowed = "".join(str(n) for n in range(1, symbols + 1))
    bad = sorted({ch for ch in raw if ch not in allowed})
    if bad:
        return (f"Only the digits 1 to {symbols} are allowed "
                f"(found {' '.join(bad)}).")
    return None


def format_history(history):
    """Lay the accepted guesses out as a small table."""
    if not history:
        return "No guesses yet."
    width = max(len("Guess"), max(len(guess) for guess, _, _ in history))
    lines = [f"{'#':>3}  {'Guess':<{width}}  {'Exact':>5}  {'Partial':>7}"]
    for number, (guess, exact, partial) in enumerate(history, start=1):
        lines.append(
            f"{number:>3}  {guess:<{width}}  {exact:>5}  {partial:>7}")
    return "\n".join(lines)


class Mastermind:
    def __init__(self, difficulty=DEFAULT_DIFFICULTY, code=None):
        if difficulty not in DIFFICULTIES:
            raise ValueError(f"Unknown difficulty: {difficulty!r}")
        cfg = DIFFICULTIES[difficulty]
        self.difficulty = difficulty
        self.length = cfg["length"]
        self.symbols = cfg["symbols"]
        if code is None:
            code = [str(random.randint(1, self.symbols))
                    for _ in range(self.length)]
        self.code = list(code)
        self.history = []
        self.turns = cfg["turns"]
        # "playing" -> "won" | "lost" | "quit". Once it leaves "playing"
        # it never changes again.
        self.state = "playing"

    def submit(self, raw):
        """Score one guess and update the game. Returns (exact, partial).

        A malformed guess raises ValueError before anything is changed, so
        it never uses up a turn or reaches the history.
        """
        if self.state != "playing":
            raise GameOver(f"The game is over ({self.state}).")
        problem = validate_guess(raw, self.length, self.symbols)
        if problem:
            raise ValueError(problem)
        exact, partial = feedback(self.code, list(raw))
        self.history.append((raw, exact, partial))
        self.turns -= 1
        if exact == len(self.code):
            self.state = "won"
        elif self.turns == 0:
            self.state = "lost"
        return exact, partial

    def quit(self):
        """End the game early. Has no effect once the game is already over."""
        if self.state == "playing":
            self.state = "quit"

    def run(self):
        print(f"Mastermind — enter {self.length} digits from 1 to "
              f"{self.symbols}, or q to quit.")
        while self.state == "playing":
            try:
                raw = input(f"{self.turns} turns left > ").strip()
            except EOFError:
                self.quit()
                break
            if raw.lower() == "q":
                self.quit()
                break
            try:
                exact, partial = self.submit(raw)
            except ValueError as problem:
                print(problem)
                continue
            print("Exact:", exact, " Partial:", partial)
            print(format_history(self.history))
        self.report()

    def report(self):
        """Print how the game ended."""
        if self.state == "won":
            print(f"Cracked the code in {len(self.history)} guesses!")
        elif self.state == "lost":
            print("Out of turns. The code was", "".join(self.code))
        else:
            print("Game ended before the code was cracked.")
