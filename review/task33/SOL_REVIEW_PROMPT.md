# Review prompt: Task 33 build (read-only dashboard)

You are an independent adversarial reviewer working read-only, not an authority. You accepted the proposal at re-review 7 (`DASHBOARD_PROPOSAL.md`). This is the build. Attached are:
- the local gate record, with the Linux CI sandbox results and two defects the CI found (G33-3, G33-4);
- `src/aqt/dashboard.py`, `scripts/dashboard.py`;
- the systemd unit and timer, and the install script;
- the CI step and the RUNBOOK section;
- the tests.

Check:
1. Does the build meet each acceptance item of the proposal (section 4), and is any claim in the gate record unsupported?
2. Security: can the page builder change the app's state, leak the token, or produce active content? Is G33-3's repair sound, given `CAP_DAC_READ_SEARCH`? Does any other path visible in the unit hold a secret that the page could show?
3. Honesty of the page: can any panel show a number or status that the files do not support? Check the four input states, the ledger handling and the health rule.
4. Does the install leave the paper app and its checkout untouched?

Keep to findings that matter. Verdict ACCEPT or FIX. Give findings stable IDs T33-n, each with severity, evidence and a minimal correction.
