# §16 different-model code review — evaluation-attempt counting

**Reviewed:** PR #6, branch `feat/evaluation-attempt-counting`, commit `c7b116c`
against `main` at `93c3924`. Two added files, 669 insertions, nothing else.
**Reviewer:** Claude, observed model ID `claude-fable-5-1`, read-only.
**Author of the reviewed code:** Claude, observed model ID `claude-opus-5`.
**Verdict:** `REVISION_REQUIRED`
**Recorded:** 2026-09-21

This is the verbatim record of the review, committed before it is cited, as
`AGENTS.md` requires. It is an AI review. It carries no scientific or governance
authority, does not satisfy the human prong of Constitution §16, and is not
acceptance of anything.

## Validation the reviewer ran independently

| Command | Result |
| --- | --- |
| `./.venv/Scripts/python.exe -m pytest tests/unit/test_attempts.py -q` | 30 passed, exit 0 |
| `ruff format --check .` | 62 formatted |
| `ruff check .` | pass |
| `mypy src` | 30 files, no issues |
| `python -m pytest` | 1139 passed, 4 skipped |
| `lint-imports` | 5 kept, 0 broken |

Reported by the reviewer rather than hidden: its first `python -m lint_imports`
invocation failed as a wrong module name; the CI executable ran fine. Recorded so
it is not mistaken for a tool gap.

## Break attempts, with exact inputs

| Probe | Input | Result |
| --- | --- | --- |
| T1 | `start_attempt(id="attempt-0001", family="family-one")`, then same id with `family="family-two", cycle="C2"` | second returns `None`; `family-two` lifetime = **0**. Silent loss |
| T2 | `append_entry` a started record with `partition="lockbox"` | `recorded_attempts`=1, `cycle_attempts`=0, `lifetime`=0, `excluded`=0. Recorded but counted nowhere |
| T2b | same, payload lacking `family` | same silent drop |
| T3 | families `"family-one"`, `"family-one "`, `"Family-One"` | lifetime for `family-one` = **1** of 3 |
| T4 | two threads, `Barrier(2)`, same `attempt_id` | both append; `cycle_attempts`=**2** for one id |
| T5 | child process `start_attempt(...)` then `os._exit(1)` | parent counts **1**, ledger intact. Crash-safety **holds** |
| T5b | truncate last 10 bytes of T5's ledger | `read_entries` raises `LedgerError`; `start_attempt` refuses to append. Fails closed |
| T6 | `finish_attempt` `completed` then `aborted` for one id | both accepted; count unchanged |
| T7 | exploration attempt in `C0`, counting `C1` | `excluded`=0, lifetime=1; docstring implies otherwise |
| T8 | `attempt-btc` symbols `("BTC",)`, `attempt-eth` `("ETH",)` | counts 2 (overcount; conservative) |

**Crash-safety, analytically.** `append_entry` writes, flushes, and `fsync`s
while holding the lock, and `start_attempt` returns only afterwards, so every
crash point after return is after fsync. Crash mid-write leaves a torn line and
every reader raises: no silent undercount, but counting is unavailable until a
human repairs the file. `ledger.py` fsyncs the file but not the directory, so OS
power loss on a freshly created ledger can lose the file on POSIX — pre-existing
in `ledger.py`, not introduced by this change. The claimed property holds, with
the torn-write caveat.

## Findings

**F-1 `BLOCKER` — contradicting redelivery is silently discarded (undercount).**
`start_attempt` returns `None` for any already-seen `attempt_id` without
comparing the payload (T1). `AttemptError`'s own docstring promises an error when
a record "contradicts one already recorded"; the code never checks. A caller
whose id generator collides, or that keys ids by trial point rather than
occasion, loses attempts silently — exactly the missing-attempt error the module
exists to prevent.

**F-2 `BLOCKER` — read-side silent drop of started records.** `attempt_counts`
filters on `partition` and `family` membership, so any started record with an
unknown partition or a missing field (T2, T2b) vanishes from all four counts. The
claim "every count reads only those records" is true; "an attempt cannot be
recorded but not counted" is false. Fail closed instead.

**F-3 `NON-BLOCKING` — idempotency claim is false under concurrency.** The
dedupe read happens outside the ledger lock, so two concurrent starts with one id
both append (T4). The direction is overcount, so the hurdle is not lowered, but
the documented invariant is wrong, and a consumer treating `None` as
"already started, skip" would run two evaluations.

**F-4 `NON-BLOCKING` — identifier drift splits lifetime accounting
(undercount).** `family` and `cycle` are free text, and `attempts._require_text`
accepts padding and case variants that `ledger._require_text` rejects (T3).

**F-5 `QUESTION` (owner) — `PARTITION_TRAINING` has no frozen referent.**
`protocol_v1.yaml:64-66` defines exactly `exploration`, `confirmation`, and
`lockbox`; line 68 `exploration_may_enter_training_folds` is a fold rule, not a
partition, and `training` appears nowhere as a partition. Further, §9 excludes
exploration "because it is confined to exploration data" — a fact about the data
mounted, verifiable only by the engine that mounted it, not by a caller-supplied
label. A research caller labelling a confirmation run `exploration` lowers `N`.
Not fixable inside this module.

**F-6 `NON-BLOCKING` — uncited governing clause, and an unreconciled
predecessor.** Constitution §9 line 106, "If no frozen effective-count method
exists, raw count is used", is the clause that makes these raw counts
load-bearing and is not cited. Separately, `preregistration.FamilyTrialCounts`
already positions `recorded_trials` as the §9 count; the repository now has two
record types each claiming that role, with no cross-link, and `D-17` does not
choose between them.

**F-7 `NON-BLOCKING` — misattributed citation.** `S0 = sqrt(V) * A(N)` is
attributed to `protocol_v1.yaml:227-233`, which contain only `series`,
`minimum`, `effective_trial_count_method`, and `fallback`. Monotonicity of `A`
in `N` the reviewer verified by exact argument, so the conclusion stands; the
formula's source in that citation is `UNVERIFIED_EXTERNAL_ASSUMPTION`.

**F-8 `NON-BLOCKING` — what should have been built.** No consumer or enforcement
point exists: "count when evaluation begins" is a calling convention. Nothing
stops evaluation running without `start_attempt`, or reading data before it. No
ledger location is fixed anywhere, so "lifetime accounting persists" holds only
if one file spans cycles, which nothing binds. The natural artifact is an
experiment-engine hook or context manager that acquires data only after the
record is durable.

**F-9 `NON-BLOCKING` — minor semantic gaps.** Contradictory outcomes accepted
(T6); `excluded_exploration_attempts` docstring omits its cycle scope (T7);
per-leg splitting overcounts and cannot be prevented here (T8, noted only);
`start_attempt` raises `LedgerError`, not `AttemptError`, on a damaged ledger,
undocumented.

**F-10 `NON-BLOCKING` — untested docstring claims.** No test for: contradicting
redelivery; unknown or missing-field started records; concurrent starts; real
process death — `test_attempt_counts_even_when_evaluation_raises` raises *after*
the call returns in-process, which cannot fail, so it does not test crash safety;
padded or case-variant identifiers; malformed `protocol_hash`; exploration in
other cycles against lifetime; `recorded_at_utc=None`; damaged-ledger behaviour.

**F-11 §16 ruling.** Lines 147-152 enumerate six components and on the plain text
this module is none of them; the `preregistration` analogy holds as far as the
text goes, and precedent counsels reading the enumeration literally. But
"protocol-enforcement logic" is the nearest category and this module is the
designed sole source of `N` for a monotone hurdle. Ruling: **not applicable to
the module as it stands** (no consumer, no decision), and **applicable the moment
a DSR or promotion-gate consumer binds to these counts**, because the count then
becomes part of the promotion gate's input contract. The reviewer recommends the
owner treat it as covered now. Human PR review is required before merge
regardless; AI seniority replaces neither prong.

**F-12 Boundary claims — verified true.** No budget comparison, no
`trial_accounting` read, no eligibility output. Hashes are accepted as any 64-hex
and never checked against `FROZEN_HASHES.json`, so "binds no hash" is true, and a
wrong `protocol_hash` is also recorded without complaint. The only I/O is the
ledger path; imports are limited to `aqt.core.ledger`; import-linter contracts
kept.

## §9 clause mapping

| Frozen clause | As implemented |
| --- | --- |
| "Count when evaluation begins" | A calling convention only (F-8) |
| "aborted evaluated runs count / All failures count" | Outcomes never read; verified T5, T6 |
| "Lifetime family accounting persists" | Within one ledger file only (F-4, F-8) |
| "If no frozen effective-count method exists, raw count is used" | Uncited (F-6) |
| "Exploration is not a registered trial…" | A caller-supplied label (F-5) |

## Verdict and remaining decisions

`REVISION_REQUIRED`. F-1 and F-2 are undercount channels that contradict the
module's stated purpose. Right conclusion, wrong reason: the crash-safety
mechanism is sound; the counting contract around it is not.

**Human decisions:** F-5 (partition vocabulary, and who sets the label), F-6
(which record type is the §9 raw count; `D-17`), F-11 (§16 scope), F-4 (whether
`family` binds to the preregistered hypothesis record).

**Not authorized by this review:** merging PR #6, editing either file, any
consumer binding `N` into DSR, any effective-count method, calibration,
confirmation or lockbox access, promotion, trading.
