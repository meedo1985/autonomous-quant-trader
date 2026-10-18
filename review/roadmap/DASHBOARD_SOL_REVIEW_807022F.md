<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-18. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a14e52-d0b9-75d3-8b36-bdee3efcef73. Tokens used: 64,576. Packet built from dashboard-proposal 807022f (git show only): prompt DASHBOARD_REVIEW_PROMPT.md, DASHBOARD_PROPOSAL.md, deploy/aqt-paper.service, deploy/RUNBOOK.md lines 1-45, scripts/run_forward_paper.py lines 95-115, src/aqt/app/paper_loop.py as_mapping, src/aqt/app/state.py lines 270-300, pyproject.toml import-linter section. The reviewer cited files beyond the packet by GitHub URL. -->

# Sol review of the dashboard proposal at 807022f

## Review (final message, verbatim)

**Verdict: FIX.** The dashboard is a reasonable read-only feature, but the proposal needs a concrete permission model and more precise rules for what each panel can claim before approval. Nothing in these findings calls for rejecting the task.

- **DB-1 — High — Read-only access is not yet enforceable.** The [installer](https://github.com/meedo1985/autonomous-quant-trader/blob/main/deploy/install.sh) creates `/var/lib/aqt` with mode `700`, so the proposed separate account cannot read the data as described. Running it as `aqt`, or granting broad write access, would let a dashboard fault change account files. **Correction:** Specify a dedicated generator account with read and directory-traverse access only to the required inputs, no write access to app data, code, deployment records, or service controls, and write access only to its output directory. Give the HTTP process a separate account that can read only the finished page. Verify these permissions on the installed units; the proposed file-open test alone cannot establish them.

- **DB-2 — High — File content can become active HTML.** Incident text, refusals, and other report strings are inserted into an HTML/SVG page, but the proposal does not require escaping. A crafted log value could run in the owner’s browser through the tunnel. **Correction:** Escape every file-derived text and attribute value, validate plotted numbers, and add a synthetic malicious-string acceptance case. A restrictive content policy is useful additional protection.

- **DB-3 — Medium — “Localhost only” needs an explicit binding and serving rule.** Python’s command-line `http.server` [binds all interfaces by default](https://docs.python.org/3.12/library/http.server.html). A generic static server can also serve files other than `index.html` from its directory. The SSH tunnel creates access for processes on the owner’s computer and server-local clients, so “no new attack surface” overstates the case. **Correction:** Require a verified `127.0.0.1` server bind, an explicit loopback bind on the tunnel’s local end, and serving from a dedicated directory containing only the page. Add a check that the server is unreachable on the server’s external interface.

- **DB-4 — Medium — Partial writes and bad data need distinct outcomes.** The [report writer](https://github.com/meedo1985/autonomous-quant-trader/blob/main/scripts/run_forward_paper.py) appends JSONL while the timer may read it; bars and incidents can also change between reads. “No data” for every missing or empty file does not cover an incomplete last line, malformed older record, or permission failure. **Correction:** Read complete newline-terminated records, distinguish absent, pending partial, and invalid or unreadable data, show source timestamps, and replace the generated page atomically. Test a concurrent append and a corrupt record.

- **DB-5 — Medium — The health panel could imply the service is healthy when it has stopped.** A refusal or failed fetch may produce no new forward report; the latest `final_mode` then describes an earlier step. A bar can be under two hours old even when the current step refused. **Correction:** Label the values as the *last reported step*, show separate ages for the report and bar, and make a stale report or a reported refusal visibly unknown or unhealthy. Do not equate “bar recent” with “service running.”

- **DB-6 — Medium — `final_balances` are not an equity series.** The [report fields](https://github.com/meedo1985/autonomous-quant-trader/blob/main/src/aqt/app/paper_loop.py) provide asset balances, not a valued equity figure; BTC position and USDT cash also have different units. **Correction:** Show the two balances with units on separate scales. Show simulated USDT equity only when a defined, time-matched price is available; otherwise omit that line rather than inventing a value.

- **DB-7 — Medium — The `L-02` date would imply more certainty than the count supports.** The [count](https://github.com/meedo1985/autonomous-quant-trader/blob/main/src/aqt/app/forward.py) is based on daily equity returns and can be null or use a fallback method. Effective sample size can change as returns accumulate, so extrapolating today’s pace to a calendar completion date is unreliable. The [loss-bound explanation](https://github.com/meedo1985/autonomous-quant-trader/blob/main/review/pre-deployment/LOSS_BOUND_DEFAULTS.md) also says the fallback is not the same quantity as the primary method. **Correction:** Remove the date estimate. Show raw decisions, effective count when available, method, reason when unavailable, and the 240 target as a waiting condition rather than evidence of an edge.

- **DB-8 — Medium — Two labels claim more than their sources establish.** Activity fields are totals for a *step*, which can process hours spanning multiple days; assigning all counts to the report’s `at` day would be wrong. `/etc/aqt/deployments.jsonl` records the latest approved commit, not proof that a process is currently running it; the startup check occurs before the report is written. **Correction:** Label activity “per reported step” unless timestamped events support daily counts, and label the code identity “latest approved commit.” Only say “running commit” if a separate current-process check supports it.

- **DB-9 — Low — Governance is broadly right; the Task 32 reuse promise is premature.** [Constitution §16](https://github.com/meedo1985/autonomous-quant-trader/blob/main/docs/RESEARCH_CONSTITUTION.md) lists protected components, and a presentation-only dashboard is outside that list. The proposal should say this conclusion depends on the implementation staying outside those components; voluntary different-model and human PR review is sensible. Task 32 may use overlapping inputs, but its summary requirements have not been established here. **Correction:** Describe reuse as an option after Task 32’s requirements are known, and drop the fixed “one session, 300–400 lines” promise as an acceptance assumption.

The acceptance list should add the permission, loopback, escaping, partial-write, and labeling checks above. Those changes make the proposed build reviewable without expanding it into a control surface or a second reporting framework.

## Adjudication (Claude Opus 5.5, `claude-opus-5-5`, 2026-10-18)

DB-1 checked locally: `deploy/install.sh:18` creates `/var/lib/aqt` with mode `700`. Every finding is accepted; the proposal is revised in the same commit.

| ID | Severity | Decision | Change to the proposal |
|---|---|---|---|
| DB-1 | High | Accept | Two accounts: `aqt-dash` (read-only ACLs on the inputs, writes only its own directory) and `aqt-web` (reads only the page). Permission checks are runbook steps on the server. |
| DB-2 | High | Accept | Escape all file-derived text and attributes, check plotted numbers, CSP without scripts; malicious-string acceptance case. |
| DB-3 | Medium | Accept | Explicit `--bind 127.0.0.1` and dedicated directory; loopback-bound tunnel; external-interface check; the "no new attack surface" claim replaced by what the tunnel does add. |
| DB-4 | Medium | Accept | Complete records only; four states (absent, pending, invalid or unreadable, valid); source times shown; atomic page replacement; tests for concurrent append and corrupt record. |
| DB-5 | Medium | Accept | "Last reported step" label; separate report and bar ages; red on a stale report, a stale bar or a refusal. |
| DB-6 | Medium | Accept | No equity line; BTC and USDT balances on separate scales with units. |
| DB-7 | Medium | Accept | No `L-02` completion date; method and unavailability reason shown; labelled a waiting condition. |
| DB-8 | Medium | Accept | "Per reported step" and "latest approved commit" labels. |
| DB-9 | Low | Accept | §16 reading conditioned on staying outside the listed components; Task 32 reuse left open; size no longer an acceptance assumption. |

No finding is left unrepaired.
