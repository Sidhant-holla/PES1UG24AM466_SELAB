# Lab 5 – Static Code Analysis

**Name:** Sidhant Holla
**SRN:** PES1UG24AM466
**Assigned repo:** `L5_45_ticket_booking_system`
**Script:** `ticket_booking_system.py` — a movie theatre seating and ticketing manager

## Contents

| File | What it is |
|---|---|
| `ticket_booking_system.py` | The cleaned script. Pylint 10.00/10, Bandit 0 issues, Flake8 clean. |
| `issues.md` | The issue table: 20 findings with tool, code, severity, line and fix. |
| `reflection.md` | Answers to the four reflection questions. |
| `reports/before/` | Pylint, Bandit, Flake8 and program output from the original file. |
| `reports/after/` | The same four, regenerated from the cleaned file. |

## Results

| Tool | Before | After |
|---|---|---|
| Pylint | 5.37 / 10 | **10.00 / 10** |
| Bandit | 5 issues (2 High, 1 Medium, 2 Low) | **0 issues** |
| Flake8 | 7 issues | **0 issues** |

## Reproducing

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install pylint bandit flake8

python ticket_booking_system.py
pylint ticket_booking_system.py > pylint_report.txt
bandit -r ticket_booking_system.py > bandit_report.txt
flake8 ticket_booking_system.py > flake8_report.txt
```

## Commit history for this lab

The fixes are split one commit per tool, so each can be reviewed on its own:

1. Baseline — original script and the three "before" reports
2. Bandit fixes — `eval`, MD5, `os.system`, weak PRNG, bare `except`, hardcoded secret
3. Pylint fixes — mutable default argument, naming, docstrings, unused variables, refactors
4. Flake8 fixes — remaining line-length issues
5. After reports, issue table and reflection
