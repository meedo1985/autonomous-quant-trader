# Review prompt: dashboard proposal (Task 33)

You are an independent adversarial reviewer working read-only, not an authority. The owner asked for a review of the attached proposal before deciding whether to approve it. Nothing is built yet.

Attached are:
- the proposal;
- the forward paper service unit;
- the runbook's server-security section;
- the forward report writer (`scripts/run_forward_paper.py`, lines 95-115) and the report fields (`src/aqt/app/paper_loop.py`, `as_mapping`);
- the account file names (`src/aqt/app/state.py`);
- the current import-linter contracts.

Check:
1. **Security.** Can the design expose the trading server, its files or the deployment record more than today? Consider the localhost web server, the tunnel, the timer account's permissions, HTML built from file contents (escaping), and file reads racing the service's writes.
2. **Read-only claim.** Is there any path by which the dashboard could change the app's state or behaviour?
3. **Honesty.** Could any panel mislead the owner? For example, the `L-02` date estimate, equity shown from paper balances, or "no data" handling.
4. **Scope and size.** Is the design the simplest that meets the need? Is anything missing that the acceptance list should require?
5. **Governance.** Is "not §16 protected" a defensible reading, and is the relation to Task 32 stated correctly?

Keep to findings that matter for the owner's decision or for the build. Verdict ACCEPT (approvable as written), FIX (approvable after stated changes) or REJECT. Give findings stable IDs DB-n, each with severity, evidence and a minimal correction.
