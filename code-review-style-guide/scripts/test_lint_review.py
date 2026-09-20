#!/usr/bin/env python3
"""Regression test for lint_review.py.

Two calibration fixtures, both taken from the review thread this skill came from:

  fixtures/bad.py   -- code exhibiting every mechanically detectable anti-pattern.
                       Expect a substantial number of findings.
  fixtures/good.py  -- code that follows the style guide. Expect ZERO findings.
                       False positives are the failure mode that makes a triage
                       tool worthless, so this direction matters more.

Also asserts the scanner reports nothing on itself, and that the diff mode finds
only the lines a patch adds.

    python3 test_lint_review.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCANNER = HERE / "lint_review.py"
FIXTURES = HERE / "fixtures"

MIN_BAD_FINDINGS = 20


def run(*args: str, stdin: str | None = None) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(SCANNER), *args],
        capture_output=True,
        text=True,
        input=stdin,
        check=False,
    )
    return proc.returncode, proc.stdout + proc.stderr


def main() -> int:
    failures: list[str] = []

    def expect(condition: bool, label: str, detail: str = "") -> None:
        if condition:
            print(f"  ok    {label}")
        else:
            print(f"  FAIL  {label}{': ' + detail if detail else ''}")
            failures.append(label)

    print("bad fixture -- should report many findings")
    code, out = run(str(FIXTURES / "bad.py"))
    expect(code == 1, "exit code is 1", f"got {code}")
    count = out.count(": [P")
    expect(
        count >= MIN_BAD_FINDINGS,
        f"at least {MIN_BAD_FINDINGS} findings",
        f"got {count}",
    )
    for rule in ("broad-except", "mutable-default", "lazy-import", "single-use-helper", "del-param", "no-log-prefix"):
        expect(rule in out, f"detects {rule}")

    print("good fixture -- must be clean")
    code, out = run(str(FIXTURES / "good.py"))
    expect(code == 0, "exit code is 0", f"got {code}")
    expect("clean" in out, "reports clean", out.strip()[:200])

    print("scanner -- must be clean on itself")
    code, out = run(str(SCANNER))
    expect(code == 0, "exit code is 0", f"got {code}")
    expect("clean" in out, "dogfoods clean", out.strip()[:200])

    print("diff mode -- only added lines reported")
    patch = (
        "--- a/thing.py\n"
        "+++ b/thing.py\n"
        "@@ -1,3 +1,6 @@\n"
        " import os\n"
        " def f():\n"
        "-    return 1\n"
        "+    try:\n"
        "+        return 1\n"
        "+    except Exception:\n"
        "+        pass\n"
    )
    code, out = run("--diff", "-", stdin=patch)
    expect(code == 1, "exit code is 1", f"got {code}")
    expect("thing.py:4" in out or "thing.py:5" in out, "reports the added except block", out.strip()[:200])
    expect("thing.py:1" not in out, "does not report untouched context lines")

    print("min-severity gate")
    code, out = run("--min-severity", "P0-BLOCKER", str(FIXTURES / "bad.py"))
    expect("P3-STYLE" not in out, "drops P3 findings")
    expect("P0-BLOCKER" in out, "keeps P0 findings")

    print()
    if failures:
        print(f"{len(failures)} check(s) failed: {', '.join(failures)}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
