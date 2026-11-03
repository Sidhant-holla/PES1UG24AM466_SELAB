from collections import Counter


def feedback(code, guess):
    """Return (exact, partial) for a guess against the secret code.

    Each position in the code can be counted at most once. Exact matches
    are resolved first. Whatever is left over on both sides is then paired
    off symbol by symbol to give the partial matches.
    """
    exact = sum(c == g for c, g in zip(code, guess))

    code_left = Counter(c for c, g in zip(code, guess) if c != g)
    guess_left = Counter(g for c, g in zip(code, guess) if c != g)
    partial = sum(min(code_left[s], guess_left[s]) for s in guess_left)

    return exact, partial
