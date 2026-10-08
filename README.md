# Kilo Bridge Employment Package

> **Complete Guide**: For detailed instructions on running the 24/7 autonomous loop, configuration, screening logic, and audit trails, please see [**USER-GUIDE.md**](USER-GUIDE.md).

This package provides a production-grade 24/7 autonomous multi-portal employment automation engine spanning Naukri, Foundit, Indeed, and LinkedIn powered by free OpenCode + NVIDIA Nemotron-120B Super.

## 24/7 Autonomous Daemon (Recommended)

To run the continuous 24/7 autonomous cycle:

```powershell
powershell -ExecutionPolicy Bypass -File .\run-247.ps1
```
Or double-click `run-247.bat`.

## Client prerequisites

- Windows PowerShell 5.1 or PowerShell 7
- Python 3.11+ and Node.js 20+
- Google Chrome with the Agent360 extension installed and connected
- The required job-site sessions already signed in, in the Chrome profile attached to Agent360
- `@agent360/browser-mcp`; install into this package with `-InstallMcp` if it is not already present
- OpenCode CLI configured with the Agent360 browser MCP

The runner never enters passwords or OTPs. Sign in manually before running. Browser actions use the Agent360 MCP interface only.

## Run

Use the canonical Downloads copy (the command below keeps the same `-Launch` interface):

```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\Admin\Downloads\kilo-bridge-setup\kilo-bridge-setup.ps1" -InstallMcp
Copy-Item "C:\Users\Admin\Downloads\kilo-bridge-setup\candidate-profile.example.json" "C:\Users\Admin\Downloads\kilo-bridge-setup\candidate-profile.json"
# Set resume_path to the candidate's resume PDF and its real SHA256 in
# candidate-profile.json. That PDF is the single source of truth for all facts.
powershell -ExecutionPolicy Bypass -File "C:\Users\Admin\Downloads\kilo-bridge-setup\kilo-bridge-setup.ps1" -Launch
```

The setup/install step is allowed before candidate data is configured. `-Launch` requires a
hash-verified resume PDF and that the resume yields at least two skills for the match gate. It prints every candidate fact it can confirm, and every
fact it cannot, before the agent starts. There is no separate extraction or preparation step:
running `-Launch` is the whole workflow.

`-Launch` validates the local runtime, MCP package, candidate pointer and resume hash, parses the resume, then starts the project-local `employment-mission` OpenCode agent with the mission documents and existing ledger attached. Its OpenCode permission rules allow `browser_execute_script` - the required interactive path, because the mouse dispatch path times out at 1500 ms per call on this machine - while retaining the Agent360 tab-list/switch tools required to activate a session tab before interaction. It uses NVIDIA Nemotron 3 Super 120B for tool use and does not run deterministic lane scripts in place of the agent. Each launch archives the previous output/log, records fresh output, then rejects a run that violates the list/navigate/activate/screenshot startup sequence, lacks a fresh local screenshot or ledger row, emits malformed output, omits the required report headings, or records an `APPLIED` row without a receipt that resolves inside `evidence\employment-lane\`. Output and run log are saved to `evidence\employment-lane\mission-agent-output.txt` and `mission-agent-run.log`. A passing runner integrity check is not a release certification: review every lane's screenshots and ledger entries before shipment.

### Agent360 connection status and first-run recovery

Browser MCP starts its local WebSocket bridge on demand during an active OpenCode session. The extension popup may show **Not connected** while the launcher is idle or after the agent exits; that alone does not mean registration is broken. The mission follows Agent360's tab lifecycle: list session tabs once, navigate without forcing a background tab, identify and activate the target tab, then screenshot and read the page. A tab-list `Unknown` alone is not a transport failure if later navigation and screenshot work. The mouse dispatch path (`browser_click`/`browser_fill`/`browser_click_xy`/`browser_press_key` via `Input.dispatchMouseEvent`) times out at 1500 ms per call on this machine, so interactive work runs through `browser_execute_script` (JS `.click()`, set value + dispatch `input`/`change` + re-read, always `return` the result); the visible tools are a fallback for pages whose CSP blocks JS. On a timeout switch to the JS path rather than retrying the visible tool. Do not switch Chrome profiles. Keep the OpenCode agent session open while it works. A tool call or agent narrative is not proof: require a visible page receipt for each action.

### Limit one application to a specific role

The mission agent can be limited to one exact role by providing the title currently shown as `MATCHED`:

```powershell
powershell -ExecutionPolicy Bypass -File .\kilo-bridge-setup.ps1 -Launch -SubmitOne -Title "Exact matched role title"
```

The mission remains subject to the fit, candidate-fact, one-submit, and receipt gates in `MISSION-RUN.txt` and `docs\EMPLOYMENT-LANE-MISSION.md`. The title limits application submission for that run; it does not switch `-Launch` back to the deterministic lane scripts.

## Receipts and profile data

- The candidate's own **resume PDF is the single source of truth** for every candidate fact: name, phone, email, location, skills, years of experience, education, certifications and employers. `scripts\resume_facts.py` reads it at runtime, every time. There is nothing else to fill in and no pre-extraction step.
- Copy `candidate-profile.example.json` to a private `candidate-profile.json`. It is a **pointer file only**: it names the resume path and the resume SHA256. It never holds a personal value.
- A fact the resume does not state is **UNCONFIRMED**. The launcher prints every fact and its status before the agent starts, and the agent must report an unconfirmed field as BLOCKED rather than guess it.
- Recruiter questions are answered only when their exact requested fact is extractable from the resume. Unknown questions are blocked. No answer sidecar is read.
- `pypdf` is required to read the resume; the launcher installs it automatically if missing.
- Never ship a candidate's resume or answer file in a client package. Every other file in the package is off-limits as a fact source, including logs, screenshots, ledger notes, and this README.
- To see exactly what the mission will read, without starting the agent:
  `venv\Scripts\python.exe scripts\resume_facts.py <resume.pdf>`
- Mission tool directives: `MISSION-RUN.txt` and `docs\EMPLOYMENT-LANE-MISSION.md`. These direct an agent to use Agent360's existing browser tools for visible UI actions; they do not claim that every lane has already passed.
- Browser and lane code: `scripts\`
- E2E screenshots and ledger: `evidence\employment-lane\`
- No credentials are written to this package by the setup script.

The working copy includes candidate-specific evidence of one Naukri application confirmed in history. That receipt is not a client result. Profile updates, Foundit/Indeed/LinkedIn submissions, and LinkedIn comment publication still lack live receipts. Re-run against the target operator's account after the current static fixes before describing the setup as ready to ship. Do not distribute this working folder as-is: it contains local candidate data and evidence; prepare a sanitized client copy first.
