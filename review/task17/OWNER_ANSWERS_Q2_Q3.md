# Task 17 owner answers: T17-Q2 and T17-Q3

Date: 2026-09-26

The owner answered, verbatim: "yes to both T17-Q2 and T17-Q3".

The questions, as the coding AI (Claude Opus 5.5) put them, with its
recommendation of yes for both:

- **T17-Q2** (from Fable R-2): keep one fixed log file for the whole project,
  so a script cannot start a new count by choosing a new log path.
- **T17-Q3** (from Fable R-4): count a clearance only once it is on the `main`
  branch, not on whatever commit is checked out.

This records the owner's choice of design only. It does not state that the
owner reviewed the code; the section 16 human PR review of Task 17 is still
required before merge and will be recorded separately.

Effect, implemented on this branch after this record:

- The log is always `data/exploration_jobs.jsonl` under the repository root.
  Callers pass the repository root, not a log path.
- The clearance is read from the `main` branch (`git show main:<path>`). A
  clearance committed only on another branch does not count.
- The cycle id stays caller-supplied (T17-05), so a fresh cycle id still starts
  a fresh count; no cycle registry exists yet.
