# R-14 exception for the two later C2 modules: proposal rev 2 (full replacement of rev 1)

**Author:** Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-31. This is AI drafting and not an authority. **Status: INACTIVE PROPOSAL, UNREVIEWED (rev 2).** Nothing frozen is changed. It binds only as a row of the owner's signed C2, after the required human review. R19-2 requires a two-family re-check before the owner decides.

**Answers:**
- `SOL_REVIEW_23300C4.md` (gpt-6-sol): FIX, R14A-S-1..5;
- `ASTRA_REVIEW_23300C4.md` (gpt-6-astra): FIX, R14A-A-1..5.

Both were read in full. Rev 1 (`PROPOSAL.md`, 23300c4) is replaced whole.

**Direction (owner, 2026-10-31):** answering PFS-S-1, "Exception like Q4 (Recommended)": one narrow R-14 exception covering the Q4 lockbox module and a confirmation module. Background is in rev 1 §0, which stands.

## 1a. Dispositions

| ID | Disposition | Where |
|---|---|---|
| **R14A-S-1 ~ R14A-A-2** (BLOCKER; "only loads, checks, calls, records" does not stop alignment or filtering from changing a result) | **Accepted.** The claim is deleted. Each module now carries an explicit **input-to-record contract** taken from signed text, with tests at the consumer boundary. | item 4, item 5 |
| **R14A-A-1** (BLOCKER; the lockbox module must implement D-20 A4's own bootstrap, so "defines no statistic" cannot hold) | **Accepted.** The modules may implement **rules the signed C2 states**, reusing existing bound primitives wherever one fits. The accompanying R-8 extension is named. Not every statistical implementation is frozen at `AQTQ1`, and §2 says so. | item 4, item 8, §2 |
| **R14A-S-2 ~ R14A-A-5** (BLOCKER / NON-BLOCKING; the row gives no execution identity or data boundary) | **Accepted.** R-14a is stated to be **code placement only**. Each entry point is bound to its identity, data interval, read gate and output boundary. The cross-module import allowance is removed. | items 3, 6 |
| **R14A-S-3** (BLOCKER; a beacon seed copied into a trial record would pass) | **Accepted.** The confirmation module verifies the post, the round, the beacon signature and the derived seeds itself, with `seed_disclosure`'s failure rule. | item 7 |
| **R14A-S-4 ~ R14A-A-3** (NON-BLOCKING / BLOCKER; "cannot be tuned" and "caught by §16" overclaim) | **Accepted.** The residuals are rewritten. | §2 |
| **R14A-S-5 ~ R14A-A-4** (QUESTION / NON-BLOCKING; a signature is not evidence of time) | **Accepted, using Astra's existing chain.** The time anchor is the accepted C2 declaration post (DRAFT §2.0 via O-6a), through `protocol_hash`, to the two module hashes, to the loaded bytes. This chain is verified and logged before each evaluation. No new timestamp system is added. | item 2, §2 |

## 1. Proposed C2 row R-14a

> **R-14a.** R-14a changes **where code may live**, not who may read which data. Besides the code R-14 allows, a C2 evaluation may load exactly two further files: the **lockbox module** (D-20 Q4) and the **confirmation module**.
>
> 1. **Identity of the bytes.** Each is one file, merged under Constitution §16 review, with an independent different-model review record and human PR review before merge. Its SHA-256 is a row of the signed C2.
> 2. **Verified before use.** Before any read, the evaluation verifies and logs this chain: the accepted C2 declaration post (DRAFT §2.0, O-6a) → its `protocol_hash` → the module's SHA-256 row → the loaded bytes. A mismatch or an unverifiable step refuses the evaluation, and nothing is read. Nothing else is loaded from outside R-14 and this row.
> 3. **Imports.** Each imports only engine-commit modules, later object files, the standard library and pinned image libraries. Neither imports the other.
> 4. **What they may implement.** Only rules that the signed C2 states (Annex A-C, D-11, D-20 and the rows naming them). Where an engine-commit or later-object-file function implements a rule, the module calls it and does not re-implement it; the final-hour rule is `screen.py`'s `confirmation_path` (D-20 A6, Q2(ii)). A rule with no such function is implemented in the module exactly as the signed text states it. An example is D-20 A4's lockbox bootstrap, with `m ≠ n` and the `lockbox_prediction` stream. Such a rule is listed in that module's contract (item 5). No other scientific choice is permitted.
> 5. **Input-to-record contract.** For each module, the signed C2 (or the S4 text it names) states, from C-0, C-6, A4, A6 and A7:
>    - the exact timestamps read and their order;
>    - how candidate and benchmark legs are paired by day;
>    - the complete-window rule;
>    - each transformation;
>    - how availability and errors map to `UNAVAILABLE` or technical FAIL;
>    - the exact output fields.
>
>    Missing, duplicate or misaligned observations refuse; nothing is dropped, filled or re-paired silently. §16 review checks the module against this contract. Synthetic tests at the consumer boundary show each refusal, and show that the paired series reaching each statistic is exactly the contract's.
> 6. **Identity and data boundary.**
>    - The confirmation module's entry point runs only as the registered experiment-engine identity, on the confirmation partition the signed C2 allows. It returns only the C2 evaluation record.
>    - The lockbox module's entry point runs only as `lockbox_eval`, on D-11's authorised range `[S_pre, L1)`, through its read gate. It returns only what Constitution §7/§7a and D-12/D-20 allow.
>    - D-11's handoff rules and its separate Constitution §7a and access amendments still govern. §16 review checks these boundaries.
> 7. **Seeds the confirmation module must verify itself (R-13, A1b).** Before calling any gate, it verifies against the governing records, never from its caller, each of these:
>    - the accepted post;
>    - the selected drand round of the bound chain (quicknet, FP3);
>    - the beacon signature and randomness;
>    - the derived family seed (R-7) and every trial seed (R-13);
>    - the l.266 seed and the estimator seed under the signed `estimator_seed_policy`;
>    - the C-0 window and its id, and `g`.
>
>    Failure follows `seed_disclosure`'s rule: the evaluation is invalid and no gate runs. Every value and its provenance is recorded (Constitution §27).
> 8. **R-8 extension.** R-8's code binding extends to the two module hashes of this row (D-20 A6). R-8, R-13 and R-14's two checks are otherwise unchanged.

## 2. What it costs, and residuals (to disclose)

- **A later freeze for these two files.**
  - **Lost:** they are written after the qualification object's Bitcoin post (`AQTQ1`), so its earlier public anchor does not cover them.
  - **What binds them instead:** the later chain in item 2, whose public anchor is the accepted C2 declaration post. That chain is verified before every evaluation.
  - **Still lost:** the earlier freeze. A timestamp taken just before confirmation would not restore it.
  - **Not qualified:** some statistical implementation is not frozen at `AQTQ1`, for example A4's lockbox bootstrap. Reusing qualified primitives does not qualify the way the modules put them together.
- **What still limits the risk:**
  - authorised access stays restricted (item 6);
  - every rule is fixed in signed text (items 4-5);
  - a rule that has a frozen implementation must be called, not rewritten (item 4).
- **What it does not prevent:**
  - **Public prices.** D-11's historical lockbox prices are public, and D-11 says the check cannot detect strategies shaped by them. Code written after the post can reflect that knowledge, and it can change up to the moment C2 is signed.
  - **Implementation errors.** A mistake in alignment, error mapping or aggregation can change a decision while every frozen function is called correctly. Both reviewers' worked examples show this: a re-paired or dropped day turns a negative or unavailable paired Sharpe positive. §16 review and the contract tests are controls against it, not guarantees.
- **Schedule:** both modules, with their contracts and tests, must be built and reviewed before the owner signs C2. The freeze (step G) does not wait for them.
- **The alternative the owner keeps:** if every statistical implementation must precede `AQTQ1`, the modules' code must move into eligible frozen files before step G. The small pre-freeze `screen.py` change alone is then not enough (Astra's closing paragraph).

## 3. Relation to other decisions

- It replaces Q4's separate "narrow R-14 exception": one row covers both modules.
- `screen.py` must still carry, before step G, the Q5 seed parameter and the Q2(ii) `confirmation_path` (design `review/pre-freeze-screen/DESIGN.md` on branch `pre-freeze-screen-q2-q5`).
- No promotion rule, gate definition or threshold changes.

## 2b. Self-check

- One file written; all 10 findings answered.
- Deleted: "cannot change a gate, fit or statistic", "cannot be tuned", "caught only by §16", and the mutual-import allowance.
- Added: items 2 (verified chain), 5 (contract), 6 (identity and data), 7 (seed verification) and 8 (R-8 extension); the honest freeze and residual text; the owner's alternative.
