# Employment Lane Agent Rules

Use this package with the current operator's configured candidate profile and authenticated
browser session. Do not assume a specific candidate identity, Windows account, Chrome profile,
or local installation path.

## Browser tools

OpenCode launches the project-local `employment-mission` agent from
`.opencode/agents/employment-mission.md`. Its tool permissions allow `browser_execute_script`
(the primary interactive path) and the session-tab tools needed to activate the browser
before interactions. If the configured agent is unavailable, stop before browser actions.

All browser actions must use the configured Agent360 browser MCP tools. Use the exact tool
name including the `browser-mcp_` server prefix (for example `browser-mcp_browser_fill`);
a missing prefix is an invalid-tool error, not a different tool.

- `browser_execute_script` (PRIMARY for interaction), `browser_navigate`
- `browser_get_page_content`, `browser_screenshot`
- `browser_click`, `browser_fill`, `browser_click_xy`, `browser_press_key` (fallback)
- `browser_wait`

Do not use direct CDP, Playwright, Selenium, a separate debug Chrome, or a second browser
driver. Only one Agent360 client may drive the authenticated browser at a time. If the current
session is unavailable, stop and report the blocker instead of opening a new profile.

At mission start, call `browser_list_tabs` once, navigate to the requested portal without
`new_tab: true`, list tabs once to identify the target session tab, switch to it, then capture
a screenshot and read page content. The bridge is on-demand; an idle extension popup may say
“Not connected.” A single tab-list `Unknown` or empty list is not a transport outage if
navigation and screenshot work. Record the exact error and do not repeat that call blindly.
The mouse path is dead on this machine: `browser_click`, `browser_fill`, `browser_click_xy` and
`browser_press_key` dispatch through `Input.dispatchMouseEvent`, which times out at 1500 ms per
call. Use `browser_execute_script` as the primary interactive path - click by JS
(`document.querySelector(SEL).click()`, or match the control by visible text) and enter text by
setting the field's own value, dispatching input/change, then RE-READING the field (a fill that
is not read back is not a fill; always `return` the script's value). Fall back to the visible
tools only if page CSP blocks JS; on a timeout switch to the JS path rather than retrying the
visible tool, and never call `browser_solve_captcha`.
If a tool returns empty output or times out, treat it as failed until a fresh read proves the
visible state.

## Candidate facts and account access

- Use the SHA256-verified resume PDF named in `candidate-profile.json` as the sole source for
  every personal fact. The config may contain only that PDF path and its SHA256.
- Do not use prior turns, answer sidecars, account pages, logs, screenshots, ledger notes, or
  other documents as fact sources. If the resume does not explicitly state a requested fact,
  mark it BLOCKED. Never infer domain-specific years from total experience.
- Never request, read, or enter passwords or OTPs. Do not change account security settings.
  If login, MFA, CAPTCHA, or human verification appears, stop that portal and report it.
- Never make a purchase. Dismiss paid upsells only when the visible UI offers a safe way to
  continue without buying.

## Applying and public actions

- Check application history before applying. Match the exact job title and employer, and
  inspect the nearby status; unrelated page-wide words do not establish a duplicate.
- Apply only to a current role that passes the configured fit gate. Verify the live title,
  employer and form before entering answers. Stop on an unknown required answer, portal limit,
  external-site handoff, or ambiguous submit state. Never retry an ambiguous submission.
- If an apply panel closes after Save/Continue, inspect the portal's application history and
  verify the exact role, employer and sent/applied status before recording `APPLIED`.
- LinkedIn public comments must be truthful, relevant, one per post, ASCII, and contain no
  links, pricing, catalogue/demo reference, or self-promotion. Prepare a draft, but do not
  publish it unless the exact final text has explicit `SEND-APPROVED` authorization.

## Evidence and reporting

- A tool response is not proof. Screenshot the visible result after profile changes,
  applications and comments; record a ledger row for each meaningful action.
- Record only actual jobs, not page fragments such as dates, locations, filters, Save buttons,
  or employer names. Confirm title and employer from the visible card or job detail page.
- Use `APPLIED` only after visible portal confirmation or exact application-history status.
  Record ambiguous/unverified work as `BLOCKED`; record a mismatch as `NO_MATCH`.
- End each run with profile changes, confirmed applications, blockers, skipped work, and the
  ledger path. Keep package feature-coverage status aligned with receipts; a prompt directive
  or a green search run does not prove an application, profile edit, or public comment.
