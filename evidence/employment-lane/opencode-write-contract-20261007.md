# OpenCode write-contract fix — 2026-10-07

## Failed run (root cause)
The 2026-10-07 employment-mission run started the browser correctly (six
correctly-ordered Agent360 calls: list_tabs, navigate, list_tabs, switch_tab,
screenshot, get_page_content) and then died mid-append:

    Error: The write tool was called with invalid arguments:
    SchemaError(Missing key at ["filePath"])

The agent appended a ledger row with OpenCode's generic `write` tool and omitted
`filePath` (a raw-file-write contract bug). The failure was NOT in the browser or
the Agent360 MCP bridge. The hung `opencode run` process (PID 23488), with its
`@agent360/browser-mcp` child (PID 6964), was still alive afterward and held the
authenticated browser session — reaped this session.

## Fix
`scripts/lane_ledger.py` (new): append-only TSV CLI. One invocation writes exactly
one 10-column row. The CLI owns the destination, the TSV shape, the ASCII rule,
the status vocabulary (imported from `lane_tools`) and the length caps; the agent
only names fields via flags. A raw `write` against `ledger.tsv` is no longer part
of the contract.

## Wiring (contract moved into all three places the agent reads)
- `kilo-bridge-setup.ps1` prompt — "LEDGER WRITE CONTRACT" block: invoke the CLI,
  never a raw write, `--tail 1` to confirm.
- `.opencode/agents/employment-mission.md` — CLI append rule in Evidence discipline.
- `MISSION-RUN.txt` — CLI append rule in the ledger section.

## Proof (offline, `scripts/_test_lane_tools.py`, EXIT=0, 41 checks)
- row has 10 columns; date first; non-ASCII folded to ASCII ("cafe"); tab/newline
  collapsed inside a cell.
- off-vocabulary status (`DONE`) raises -> CLI exits 2 (fail-closed).
- CLI status vocabulary == `lane_tools` vocabulary.
- two appends -> two lines, 10 cols each; `--count` is read-only (exit 0).
Launcher `kilo-bridge-setup.ps1` re-parses cleanly (PowerShell AST, no errors).

## RESOLVED — resume fact-source conflict
Operator (2026-10-07) confirmed the intended candidate record is
`C:/Users/Admin/Downloads/Resume.pdf`. Only its `resume_sha256` was stale; the live
file was re-hashed and the pointer file was corrected:

    C9EA81C612A6B5E4E4A72A67F6E930B1B1EB41057691AE72548DFC7AE4542797  (stale)
    BF2FED8AFACCD67BCA87BBE50F2CF0A43956ED1025DFD068EDCB0719BC5F1394  (live, 12739 bytes)

Verified: `lane_tools.verify_candidate_resume()` -> ok=True, and
`resume_facts.py <pinned path>` reads the intended facts (EXIT=0, 86 skills). The
launcher preflight will now pass line 129 (64-hex) and line 134 (hash match).

Separately, `kilo_apply_resume.pdf` (23117 bytes, sha `C9EA81C6...`, a *different*
resume version) still sits in the package root but is NOT the pinned record. It is
not read by any runtime path; the pin is the only fact source.

## LIVE PROOF #1 — fix holds, but the model did no lane work (2026-10-07 19:06)
Live `-Launch` on the original `nvidia/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`:
- Preflight passed (resume hash + facts + agent policy) — the drift fix is proven live.
- The full six-call startup gate completed; **no** `SchemaError(Missing key at filePath)`.
- But the agent then misfired (`python.exe Resume.pdf` instead of `resume_facts.py <pdf>`,
  then cmd `dir /b` inside PowerShell) and stopped. Verdict:
  `MISSION-AGENT-VERDICT: NO FRESH LEDGER RECEIPT` (ledger unchanged). The harness was
  sound; the *model* could not follow a shell instruction.

## Model change — chosen by measurement, not preference
A read-only shell smoke (`scripts/_model_smoke.ps1`) asked three candidates to run one
command and return its stdout. `nvidia/nemotron-3-super-120b-a12b` executed it and
returned `357`; `moonshotai/kimi-k3` and `z-ai/glm-5.3-flash` produced **no tool call**
and stalled (glm also timed out in `NVIDIA-VISION-MODEL-PROBE.md`). The mission needs
correct tool/shell behaviour more than vision, so the default mission model changed to
`nvidia/nvidia/nemotron-3-super-120b-a12b` in both `kilo-bridge-setup.ps1` ($MissionModel)
and `.opencode/agents/employment-mission.md` (`model:`).

## LIVE PROOF #2 — full mission on super-120b (2026-10-07 19:19, 25 min)
Launcher verdict — the passing branch, not a failure branch:

    MISSION-AGENT-VERDICT: REPORT PRESENT - verify it before believing it
    Ledger rows for today: 22. Duration: 25 min.

What the agent actually did, all logged through `lane_ledger.py` (22 fresh rows):
- **Startup gate:** list_tabs, navigate, list_tabs, switch_tab, screenshot, read.
- **Profile lane:** read facts via `resume_facts.py` + `lane_tools.candidate_skills()`,
  then updated phone, location, profile summary and 11 key skills. Each edit has a fresh
  screenshot receipt; the typed phone/name/values were checked against the pinned resume
  (`PHONE_MATCH = True`, `NAME_MATCH = True`) — **no fabrication**.
- **Jobs lane:** gated Naukri recommended jobs (MATCHED/NO_MATCH rows, e.g. Senior Data
  Engineer/Maantic = MATCHED 2), then Foundit, then Indeed — each with receipts.
- **Applications:** none. Every apply attempt was honestly recorded `BLOCKED` (Naukri
  "no visible selection mechanism"; Foundit form elements not interactable). No `APPLIED`
  row was claimed without confirmation.
- **Report:** emitted all four required sections plus the ledger path.

It also self-recovered from isolated faults (the known CDP `Input.dispatchMouseEvent`
timeouts, one tool-name slip `mcp_browser_press_key`) by following the mission's
switch-tab-then-retry rule, instead of degenerating.

Known residual ledger defect (pre-existing, NOT from this run): 28 rows written earlier
today by an ad-hoc LinkedIn driver use `|` separators, embedded newlines and absolute
`D:\anonym\...` paths — they are not 10-column rows and are outside this package. The CLI
cannot produce such rows (10 columns enforced), so `lane_ledger.py` is the fix for the
class. Those rows are left untouched (append-only ledger).

Process hygiene held throughout: single browser owner, and `opencode`/browser-mcp reaped
clean at the end of every launch.