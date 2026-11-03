import random
from logic import feedback


class GameOver(Exception):
    """Raised when a guess is submitted after the game has already ended."""


class Mastermind:
    def __init__(self, code=None):
        if code is None:
            code = [str(random.randint(1, 6)) for _ in range(4)]
        self.code = list(code)
        self.history = []
        self.turns = 10
        # "playing" -> "won" | "lost" | "quit". Once it leaves "playing"
        # it never changes again.
        self.state = "playing"

    def submit(self, raw):
        """Score one guess and update the game. Returns (exact, partial)."""
        if self.state != "playing":
            raise GameOver(f"The game is over ({self.state}).")
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
        print("Mastermind — enter four digits from 1 to 6.")
        while self.state == "playing":
            try:
                raw = input(f"{self.turns} turns left > ").strip()
            except EOFError:
                self.quit()
                break
            if raw.lower() == "q":
                self.quit()
                break
            if len(raw) != 4 or any(ch not in "123456" for ch in raw):
                print("Enter exactly four digits from 1 to 6.")
                continue
            exact, partial = self.submit(raw)
            print("Exact:", exact, " Partial:", partial)
        self.report()

    def report(self):
        """Print how the game ended."""
        if self.state == "won":
            print(f"Cracked the code in {len(self.history)} guesses!")
        elif self.state == "lost":
            print("Out of turns. The code was", "".join(self.code))
        else:
            print("Game ended before the code was cracked.")
