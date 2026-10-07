"""_test_lane_tools.py - OFFLINE regression tests for the hardened tool layer.

No Chrome, no browser, no network. Proves the pure logic of lane_tools.py and that
the new verifying verbs exist on Agent360Client. Run:
    python _test_lane_tools.py
Exit 0 = all pass. This is the receipt that the refactor's logic is sound before
any live lane runs it.
"""
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import lane_tools as T          # noqa: E402
import agent360_client as A     # noqa: E402
import lane_apply as Apply     # noqa: E402
import lane_ledger as Ledger   # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ((" :: " + detail) if detail else ""))
    if not cond:
        FAILS.append(name)


# 1. score_card: counts real skills, gate is callers' job
n, hits = T.score_card("We need GenAI and RAG with Python and AWS", ["genai", "rag", "python", "azure"])
check("score_card counts present skills", n == 3, "n=%d hits=%s" % (n, hits))
check("score_card sees the right hits", set(hits) == {"genai", "rag", "python"})
n0, _ = T.score_card("", ["genai"])
check("score_card on empty text = 0", n0 == 0)

# 2. Resume-only recruiter answers: inject synthetic extracted facts, never read
#    the local candidate's resume or any answer sidecar in this offline fixture.
_real_candidate_facts = T.candidate_facts
T.candidate_facts = lambda: {"EMAIL": "sample@example.invalid", "YEARS_EXPERIENCE": "4"}
check("resume answer returns explicit email fact", T.answer_from_resume("What is your email address?") == "sample@example.invalid")
check("resume answer returns overall experience fact", T.answer_from_resume("How many total years of experience?") == "4")
check("resume answer blocks domain-specific years", T.answer_from_resume("How many years with sample-domain?") is None)
check("resume answer blocks unrelated personal question", T.answer_from_resume("What is your shoe size?") is None)
T.candidate_facts = _real_candidate_facts

# 2b. History confirmation is local to the exact title, not page-wide keywords.
history_ok = """Job application status
Senior Platform Engineer
Example Systems
Application sent today
Applied
07 Oct 2026
"""
entry = Apply._history_entry_for_title(history_ok, "Senior Platform Engineer")
check("history exact role with nearby sent status confirms", bool(entry and entry["status"]))
history_false_positive = """Senior Platform Engineer
Example Systems
View similar jobs
Other role application status
Applied
"""
entry2 = Apply._history_entry_for_title(history_false_positive, "Senior Platform Engineer")
check("history exact role without nearby status stays ambiguous", bool(entry2 and not entry2["status"]))
check("history unrelated applied text does not confirm absent role",
      Apply._history_entry_for_title("Applied today\nAnother role", "Senior Platform Engineer") is None)

# 2c. Duplicate matching binds an identical title to the company in the latest
#     MATCHED/APPLIED ledger row. The fixture is temporary and has no candidate data.
class _FakeLane:
    def __init__(self, ledger_path):
        self.ledger_path = ledger_path

with tempfile.TemporaryDirectory(dir=HERE) as temp_dir:
    ledger = Path(temp_dir) / "ledger.tsv"
    ledger.write_text(
        "ts\turl\tportal\trole\tcompany\tscore\tstage\tstatus\treceipt\tnote\n"
        "1\tu\tnaukri\tSenior Platform Engineer\tOld Systems\t3\tmatch\tMATCHED\tnone\told\n"
        "2\tu\tnaukri\tSenior Platform Engineer\tExample Systems\t4\tmatch\tMATCHED\tnone\tnew\n"
        "3\tu\tnaukri\tOther Engineer\tElsewhere\t4\tmatch\tMATCHED\tnone\tother\n",
        encoding="utf-8")
    fake_lane = _FakeLane(ledger)
    check("known company uses latest exact-title match",
          Apply._known_company(fake_lane, "Senior Platform Engineer") == "Example Systems")
    check("known company ignores other role rows",
          Apply._known_company(fake_lane, "Missing Engineer") is None)

# 3. wall detection: by NAME, never on length alone
check("wall detects login", T.Lane("x", "t").wall("Jobseeker's Login: Search the Best Jobs") == "jobseeker's login")
check("wall detects captcha", T.Lane("x", "t").wall("please verify you are human") is not None)
check("wall silent on a real page", T.Lane("x", "t").wall("Recommended jobs for you. Apply now. " * 50) is None)

# 4. the new verifying verbs exist on the client
for verb in ("_js", "url", "toast", "readback", "fill_verified", "find_and_click",
             "findclick", "fill_checked"):
    check("client has verb %s" % verb, hasattr(A.Agent360Client, verb))

# 5. the JS builders format without error (no live call - just the string ops)
try:
    sels = T.CARD_SELECTORS["naukri"]
    js = T._READ_CARDS_JS % (__import__("json").dumps(sels), 60)
    check("_READ_CARDS_JS formats", "querySelectorAll" in js and "naukri" not in js)
    fill = T._FILL_JS % __import__("json").dumps("2")
    check("_FILL_JS formats", "chatbot_MessageContainer" in fill and '"2"' in fill)
    check("_PANEL_Q_JS present", ".chatbot_MessageContainer" in T._PANEL_Q_JS)
    check("_SAVE_JS present", "'Save'" in T._SAVE_JS and "'Send'" in T._SAVE_JS)
except Exception as e:
    check("JS builders format", False, repr(e))

# 6. status vocabulary is the mission's exact set
check("statuses present", {T.MATCHED, T.APPLIED, T.APPLIED_STEP, T.BLOCKED,
                           T.NO_MATCH, T.RATE_LIMITED, T.FAILED, T.OK}
      == {"MATCHED", "APPLIED", "APPLIED_STEP", "BLOCKED", "NO_MATCH", "RATE_LIMITED", "FAILED", "OK"})


# 7. _fill_panel unwrap: _js already parses the JSON string to a dict, so the panel
#    helper MUST read the dict directly (the 2026-10-07 double-unwrap defect).
class _FakeClient:
    def __init__(self, ret):
        self.ret = ret
    def _js(self, expr):
        return self.ret
    def call_tool(self, name, args=None):
        return {}


elem, actual = T._fill_panel(_FakeClient({"elem": "TEXTAREA.x", "actual": "2"}), "2")
check("_fill_panel reads dict-direct", (elem, actual) == ("TEXTAREA.x", "2"), "%r" % ((elem, actual),))
elem2, actual2 = T._fill_panel(_FakeClient({"result": {"elem": "INPUT.y", "actual": "2"}}), "2")
check("_fill_panel tolerates result-wrap", (elem2, actual2) == ("INPUT.y", "2"))
elem3, actual3 = T._fill_panel(_FakeClient('{"elem":"INPUT.z","actual":"2"}'), "2")
check("_fill_panel parses a JSON string", (elem3, actual3) == ("INPUT.z", "2"))

res = T.answer_and_save(_FakeClient({"elem": "TEXTAREA.x", "actual": "2"}), "Q?", "2")
check("answer_and_save ok when readback matches", res["ok"] is True, "res=%r" % res)
res2 = T.answer_and_save(_FakeClient({"elem": "TEXTAREA.x", "actual": ""}), "Q?", "2")
check("answer_and_save NOT ok when field empty", res2["ok"] is False)

# 8. lane_ledger CLI - the write-contract fix (2026-10-07). The mission agent
#    appends rows through this CLI, never a raw `write` (which died on a missing
#    filePath). Proven offline: exact 10-col shape, ASCII folding, fail-closed
#    status, and append-only file writes reported with a running count.
class _A:
    portal = "naukri"
    source = "https://example.invalid/job"
    role = "Senior Engineer"
    company = "Example Systems"
    score = "3"
    step = "emit row"
    status = "OK"
    receipt = "evidence/employment-lane/x.png"
    note = "caf\u00e9\tcol\nnext line"
    today = "2026-10-07"


row = Ledger.build_row(_A)
check("lane_ledger row has 10 columns", row.count("\t") == 9, "%d tabs" % row.count("\t"))
check("lane_ledger keeps today first", row.split("\t")[0] == "2026-10-07")
check("lane_ledger folds non-ASCII to ASCII", Ledger._ascii("caf\u00e9").isascii())
check("lane_ledger collapses tab/newline in a cell",
      "\t" not in Ledger._ascii(_A.note) and "\n" not in Ledger._ascii(_A.note))


class _Bad(_A):
    status = "DONE"


try:
    Ledger.build_row(_Bad)
    check("lane_ledger rejects an off-vocabulary status", False)
except ValueError:
    check("lane_ledger rejects an off-vocabulary status", True)

check("lane_ledger vocab == lane_tools vocab",
      set(Ledger.VALID_STATUSES) == {T.MATCHED, T.APPLIED, T.APPLIED_STEP, T.BLOCKED,
                                     T.NO_MATCH, T.RATE_LIMITED, T.FAILED, T.OK})

import contextlib as _ctx   # noqa: E402
import io as _io            # noqa: E402

with tempfile.TemporaryDirectory(dir=HERE) as _td:
    _tmp = Path(_td) / "ledger.tsv"
    _orig = Ledger._ledger_path
    Ledger._ledger_path = lambda: _tmp
    try:
        _buf = _io.StringIO()
        with _ctx.redirect_stdout(_buf):
            r1 = Ledger.main(["--portal", "naukri", "--source", "u", "--role", "R",
                              "--company", "C", "--score", "3", "--step", "s",
                              "--status", "OK", "--receipt", "r", "--today", "2026-10-07"])
            r2 = Ledger.main(["--portal", "naukri", "--source", "u", "--role", "R",
                              "--company", "C", "--score", "3", "--step", "s",
                              "--status", "MATCHED", "--receipt", "r", "--today", "2026-10-07"])
            rc_read = Ledger.main(["--count"])
        _lines = _tmp.read_text(encoding="utf-8").splitlines()
    finally:
        Ledger._ledger_path = _orig
check("lane_ledger appends append-only (one line per row, 10 cols)",
      r1 == 0 and r2 == 0 and len(_lines) == 2
      and _lines[0].count("\t") == 9 and _lines[1].count("\t") == 9)
check("lane_ledger --count is read-only (exit 0)", rc_read == 0)


print("")
if FAILS:
    print("TESTS FAILED: %d" % len(FAILS))
    for f in FAILS:
        print("  - " + f)
    sys.exit(1)
print("ALL LANE-TOOLS TESTS PASSED")
