<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-24. CLI banner: model gpt-6-astra, reasoning effort high, sandbox read-only, session 01a16e78-46f1-73a3-9014-dacd1378d28b. Tokens used: 73,851. Prompt: review/d19-engine/FREEZE_SHEET_FP2_REVIEW_PROMPT.md (commit 299934d), reviewing 99ef780 on freeze-sheet. The reviewer's remark "exact runtime model/effort metadata was unavailable" refers to its own view; the banner above is the CLI's record. Below: the reviewer's final message, unedited. -->

# Astra review of the freeze sheet's FP2 update at 99ef780

- Findings: FS2-R1 (MINOR). Verdict: ACCEPT.
- FS2-R1 accepted and repaired in the commit that adds this record: the status line and "What it is" now state step G0's exception (G0 may run once PR #77 is merged; step G and after still wait for FULL_RUN.md step F and FP1-FP4). No finding left unrepaired.

---

**Verdict: ACCEPT**, with one non-blocking wording finding. G0 closes **FP2-R2(b)’s missing-procedure requirement**; FP2 remains operationally open until the owner executes it and its successful evidence is recorded.

Reviewed `a6ce8fd..99ef780` against launcher `500f1ff` and all five committed FP2 review/adjudication records.

**FS2-R1 — MINOR — Opening restrictions omit G0’s exception.**

- **Place:** `deploy/calibration/FREEZE_HELDOUT.md:3–5`, versus line 23.
- **Failure scenario:** The introduction says nothing touches the server until G and the procedure starts only after FULL_RUN step F. G0 now explicitly permits installation after PR #77 merges, before FP1–FP4 all hold. An owner following the introduction could unnecessarily defer installation.
- **Repair:** Qualify both introductory restrictions with the G0 exception. Keep G and subsequent steps gated on FP1–FP4. This is non-blocking because line 23 explicitly establishes the correct ordering.

The substantive checks pass:

- **Launcher agreement:** `freeze <full commit>`, `heldout <attempt> <posted hash> <round> <randomness>`, and `certify <attempt> <posted hash>` match. Freeze uses the uid-990 disposable clone while importing the run’s code from `/app`. Held-out execution and certification use `/app`.
- **Outputs and paths:** Freeze prints the verified checkout line and, on success, `qualification_object_sha256 <hash>`; the object is `/var/lib/aqt-d19/qobj-1`. Held-out launch prints Docker’s container ID and the start message. Status displays state, timestamps, exit code and chunk counts. Certification prints its acceptance result and JSON report, saved as `/var/lib/aqt-d19/certify-v1.json`; an existing report causes refusal.
- **G0 verification:** Both full commit identities, the exact origin, clean status, ownership and write permissions are checked. Successful normal output is:

| G0 command | Expected output |
|---|---|
| Clone, checkout, chmod | Normally none |
| Build `rev-parse HEAD` | Filled full merge SHA |
| App `rev-parse HEAD` | `eeaa7282e3b7c87790c162d679016c290d5f4ea5` |
| Origin | Specified GitHub HTTPS URL |
| Status | Nothing |
| `find` | Nothing; otherwise the first offending path |

The committed `find` line is correctly escaped: **one backslash before each parenthesis**. `/022` detects either group-write or other-write permission. Its successful exit alone does not establish safety; the required empty output does.

G0’s exception avoids a circular prerequisite. Step G correctly discloses its network requirement. The launcher grants bridge networking to the **whole freeze container for its lifetime**.

Validation: `git diff --check` passed; all filled shell blocks passed Dash syntax checking; a harmless argument-capture harness verified the exact `find` arguments. All 31 checksum entries, frozen manifest bindings and Constitution self-hash matched; protected artifacts were unchanged. Application tests, lint, type and import checks were N/A for this documentation-only diff.

No Ubuntu/server execution occurred. The worktree remains unchanged. Reviewer: Codex; exact runtime model/effort metadata was unavailable. This read-only report still needs committing under the repository’s review-record rule; §16 owner review remains separate.
