"""lane_ledger.py - append ONE honest employment-lane ledger row, atomically.

WHY THIS EXISTS (2026-10-07)
----------------------------
The mission agent used to append ledger rows by hand with OpenCode's generic
`write` tool. On 2026-10-07 that call shipped `content` without `filePath` and the
run died mid-append:

    Error: The write tool was called with invalid arguments:
    SchemaError(Missing key at ["filePath"])

A prose rule ("write a ledger row") is not a contract. This is the contract: the
agent NAMES the fields and this CLI owns everything fragile - the destination, the
10-column TSV shape, the ASCII rule, the status vocabulary and the length caps. The
agent never hands a raw file path/body to a generic writer again.

LAWS OBEYED
-----------
* APPEND-ONLY: the file is opened 'a' and never rewritten (ledger history is
  immutable; corrections are new rows, never edits).
* Exactly 10 tab-separated columns, one row per line, no embedded tab/newline.
* `--status` must be one of the lane_tools vocabulary, so a typo cannot mint a
  status the reports do not understand (fail-closed: BLOCKED + exit 2).
* ASCII-only cells (AGENTS.md law 10): non-ASCII is folded, not silently kept.
* A write is not proof: the caller re-reads with `--tail` to confirm (law 1).

USAGE - agent form: every value is a named flag, nothing is positional
  venv\\Scripts\\python.exe scripts\\lane_ledger.py ^
      --portal naukri ^
      --source "https://www.naukri.com/mnjuser/profile" ^
      --role - --company - --score - ^
      --step "profile audit" --status OK ^
      --receipt evidence/employment-lane/70-naukri-profile-audit-20261007.png ^
      --note "100% complete; headline verified vs pinned resume"

READ-ONLY subcommands:  --tail N | --count | --path
SAFE PREVIEW:  add --dry-run to print the row without writing it
TEST HOOK:     --today YYYY-MM-DD fixes the date (the mission never passes it)

Exit codes: 0 = row appended / read returned; 2 = BLOCKED (bad status/missing
flag/no ledger). The last stdout line is always `RESULT: ...` for the caller.
"""
from __future__ import annotations

import argparse
import io
import sys
from datetime import date
from pathlib import Path

try:
    import lane_tools as LT
except Exception as exc:  # pragma: no cover - packaging defect, reported not raised
    raise SystemExit("lane_ledger: cannot import lane_tools (%s)" % exc)


def _use_utf8_stdout():
    """Idempotent UTF-8 stdout: lane_tools already did this on import."""
    try:
        if (getattr(sys.stdout, "encoding", "") or "").lower().replace("-", "") == "utf8":
            return
        previous = sys.stdout
        sys.stdout = io.TextIOWrapper(previous.buffer, encoding="utf-8", errors="replace")
        try:
            previous.detach()
        except Exception:
            pass
    except Exception:
        pass


_use_utf8_stdout()

# The ledger status vocabulary, taken from lane_tools so there is ONE definition.
VALID_STATUSES = (
    LT.MATCHED, LT.APPLIED, LT.APPLIED_STEP, LT.BLOCKED,
    LT.NO_MATCH, LT.RATE_LIMITED, LT.FAILED, LT.OK,
)

MAX_FIELD = 900  # a note longer than this is a report, not a ledger cell.


def _ascii(value, limit=MAX_FIELD):
    """One ledger cell: ASCII-only, single-line, whitespace-collapsed, trimmed."""
    text = "" if value is None else str(value)
    text = text.replace("\t", " ").replace("\r", " ").replace("\n", " ")
    text = text.encode("ascii", "replace").decode("ascii")
    text = " ".join(text.split())
    if len(text) > limit:
        text = text[: max(1, limit - 3)].rstrip() + "..."
    return text


def _package_root():
    return LT.HERE.parent


def _ledger_path():
    """The ONE ledger this package appends to (never a caller-chosen path)."""
    return _package_root() / "evidence" / "employment-lane" / "ledger.tsv"


def _relativize(receipt):
    """Store a receipt relative to the package root when it lives inside it."""
    text = str(receipt or "")
    if not text or text == "-":
        return text or "-"
    try:
        path = Path(text)
        if path.is_absolute():
            return path.resolve().relative_to(_package_root().resolve()).as_posix()
    except Exception:
        pass
    return text.replace("\\", "/")


def build_row(args):
    """The exact TSV line for `args`. Raises ValueError on an invalid status."""
    status = _ascii(args.status, 40).upper()
    if status not in VALID_STATUSES:
        raise ValueError("status %r not in %s" % (args.status, ", ".join(VALID_STATUSES)))
    today = _ascii(args.today, 20) or str(date.today())
    cells = [
        today,
        _ascii(args.portal, 60),
        _ascii(args.source),
        _ascii(args.role),
        _ascii(args.company, 120),
        _ascii(args.score, 12),
        _ascii(args.step, 160),
        status,
        _ascii(_relativize(args.receipt), 400),
        _ascii(args.note),
    ]
    return "\t".join(cells)


def _rows(path):
    if not path.is_file():
        return None
    return [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def read_only(args):
    path = _ledger_path()
    if args.path:
        print(str(path))
        return 0
    lines = _rows(path)
    if lines is None:
        print("RESULT: BLOCKED ledger missing: %s" % path)
        return 2
    if args.count:
        print(len(lines))
        return 0
    n = args.tail if args.tail is not None else 5
    for line in lines[-n:]:
        print(line)
    print("RESULT: OK (%d rows, showing last %d)" % (len(lines), min(n, len(lines))))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="lane_ledger.py",
        description="Append one honest employment-lane ledger row (append-only TSV).")
    parser.add_argument("--portal")
    parser.add_argument("--source")
    parser.add_argument("--role")
    parser.add_argument("--company")
    parser.add_argument("--score")
    parser.add_argument("--step")
    parser.add_argument("--status")
    parser.add_argument("--receipt")
    parser.add_argument("--note", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--today")
    parser.add_argument("--tail", type=int, default=None)
    parser.add_argument("--count", action="store_true")
    parser.add_argument("--path", action="store_true")
    args = parser.parse_args(argv)

    if args.path or args.count or args.tail is not None:
        return read_only(args)

    required = ("portal", "source", "role", "company", "score", "step", "status", "receipt")
    missing = [name for name in required if getattr(args, name) is None]
    if missing:
        print("RESULT: BLOCKED missing required flag(s): %s" % ", ".join(missing))
        print("usage: lane_ledger.py --portal P --source S --role R --company C "
              "--score N --step STEP --status STATUS --receipt RECEIPT [--note NOTE]")
        return 2

    try:
        row = build_row(args)
    except ValueError as exc:
        print("RESULT: BLOCKED %s" % exc)
        return 2

    if row.count("\t") != 9:
        print("RESULT: BLOCKED internal shape error (column count != 10)")
        return 2

    path = _ledger_path()
    if args.dry_run:
        print(row)
        print("RESULT: OK (dry-run, nothing written); target -> %s" % path)
        return 0

    if not path.parent.is_dir():
        print("RESULT: BLOCKED evidence dir missing: %s" % path.parent)
        return 2

    with path.open("a", encoding="utf-8", newline="") as handle:
        handle.write(row + "\n")
    total = len(_rows(path) or [])
    print(row)
    print("RESULT: OK appended (ledger now %d rows) -> %s" % (total, path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())