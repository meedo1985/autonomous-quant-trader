# R-14 exception for the two later C2 modules (lockbox module, confirmation module): proposal

**Author:** Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-31. This is AI drafting and not an authority. **Status: INACTIVE PROPOSAL, UNREVIEWED.** Nothing frozen is changed. It binds only as a row of the owner's signed C2, after the required human review. R19-2 requires a two-family review before the owner decides.

## 0. Why, and the owner's direction

- **R-14** (owner-decided in D-20 (rest), `d20-d13-proposal/OWNER_DECISION_D20_D13.md` l.76; text in S4 `DRAFT_WORDING.md` l.152) lets a C2 evaluation load only two kinds of code: engine-commit files, and the three later object files frozen in the qualification object (`mapping.py`, `screen.py`, `heldout.py`). "The C2 evaluation's own code therefore lies in the engine commit or in a later object file."
- **D-20 Q4** (`OWNER_DECISION_D20_LOCKBOX.md` item 8): the owner chose "one separate reviewed lockbox module, its fingerprint in the signed C2, with a narrow R-14 exception". That exception's text is not yet drafted.
- **PFS-S-1** (`autonomous-quant-trader` branch `pre-freeze-screen-q2-q5`, `review/pre-freeze-screen/SOL_DESIGN_REVIEW_CEB12C3.md`, gpt-6-sol): the C2 **confirmation** coordinator is also C2 evaluation code. That means loading the confirmation partition, calling the screen's gates, the paired statistics and the C2 record. It does not exist yet, so under R-14 it would have to be in a frozen file before step G.
- **Owner direction (2026-10-31),** answering PFS-S-1: "Exception like Q4 (Recommended)". Draft one narrow exception covering both modules. Meanwhile `screen.py` gets only the small Q2(ii)/Q5 change before the freeze.

## 1. Proposed C2 row R-14a

> **R-14a.** Besides the code R-14 allows, a C2 evaluation may load exactly two further files: the **lockbox module** (D-20 Q4) and the **confirmation module**. For each file:
> 1. it is one file, merged under Constitution §16 review with an independent different-model review record; its SHA-256 is a row of the signed C2;
> 2. the evaluation verifies the loaded bytes against that SHA-256 before use, as R-14 does for later object files; nothing else is loaded from outside R-14 and this row;
> 3. it imports only engine-commit modules, later object files, the other module of this row, and the standard library and pinned image libraries;
> 4. it **defines no** gate, signal, feature, model fit, cost, event-contract, seed-derivation or statistic rule that Annex A-C, R-8 or R-13 bind. For each, it calls the engine-commit or later-object-file code that implements the rule. It only loads data, checks inputs and identities, calls that code, and writes records;
> 5. the confirmation module verifies from the trial record and the signed C2, never from its caller, every value it passes on: the l.266 seed and the estimator seed derived from it under the signed `estimator_seed_policy` (D-20 A1b), R-13's beacon-protected trial seed, the C-0 window and its id, and `g`. It records each of them (PFS-S-5);
> 6. both modules use the one final-hour rule frozen in `screen.py` (D-20 A6, Q2(ii)).

## 2. What it costs, and residuals (to disclose)

- **Weaker freeze evidence for these two files.** They are written after the qualification object's Bitcoin post (`AQTQ1`), so the posted hash does not cover them. They are bound by the signed C2 hash instead. That hash is fixed before any C2 evaluation reads confirmation or lockbox bytes, because C2 must be signed before any C2 evaluation runs.
- **What limits the risk:** item 4 keeps every scientific rule in frozen or engine code. The modules cannot change a gate, fit or statistic; they can only call them. Confirmation and lockbox data stay sealed until the signed C2 permits a read, so neither module can be tuned on them.
- **What it does not prevent:** a bug in loading, identity checks or records. That is caught only by §16 and the independent review, as for any build.
- **Schedule:** both modules must be built and reviewed before the owner signs C2. The freeze (step G) does not wait for them.

## 3. Relation to other decisions

- It replaces the separate "narrow R-14 exception" of Q4 with this one row, so there is one row for both modules, not two.
- It does not change R-8, R-13 or R-14's two checks. It changes no gate or statistic and is not a promotion rule.
- `screen.py` must still carry, before step G, the Q5 seed parameter and the Q2(ii) final-hour helper. The model fit is in `screen.py` (`walk_forward`), and item 4 forbids redefining it elsewhere.

## 4. Questions for reviewers

- Is item 4 precise enough to be checked at §16 review? Can "loads data, checks, calls and records" hide a statistic, for example in how the paired series are aligned?
- Does R-14a open any path for the lockbox module or the confirmation module to read data that D-11 or Constitution l.73 does not allow?
- Is binding by the signed C2 hash, instead of the posted object hash, a real weakening that needs a stronger time anchor (for example a public timestamp before the first confirmation read)?
