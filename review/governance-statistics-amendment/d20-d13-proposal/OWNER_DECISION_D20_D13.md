# Owner decision: D-20 (rest), the model-library image, the C2 seed source, and D-13

**Date:** 2026-10-13
**Authority:** The owner decided in a Claude Code session. Claude Opus 5.5 (`claude-opus-5-5`) asked the questions and recorded the answers. The AI did not choose any answer.

## Decided object

`PROPOSAL.md` revision 6, commit `5c78b8f`, in this folder.

**Reviews (all committed in this folder):**

| Reviewer | Record | Revision | Verdict |
|---|---|---|---|
| Sol (gpt-6-sol) | `SOL_REVIEW_37F20C8.md` | rev 1 | Q1 NOT READY, Q2 READY WITH FIXES, Q3 NOT READY, Q4 READY WITH FIXES |
| Fable (claude-fable-5-1) | `FABLE_REVIEW_37F20C8.md` | rev 1 | Q1–Q4 READY WITH FIXES |
| Sol | `SOL_RECHECK_2DB4D63.md` | rev 2 | Q1–Q3 NOT READY, Q4 READY WITH FIXES |
| Fable | `FABLE_RECHECK_2DB4D63.md` | rev 2 | Q1–Q4 READY WITH FIXES |
| Fable | `FABLE_RECHECK2_DBA31FB.md` | rev 3 | Q1, Q4 READY WITH FIXES; Q2, Q2b, Q3 READY |
| Sol | `SOL_RECHECK2_DBA31FB.md` | rev 3 | Q1, Q2b (a), Q3, Q4 NOT READY; Q2 READY WITH FIXES |
| Fable | `FABLE_RECHECK3_4645E0A.md` | rev 4 | Q1, Q2, Q4 READY; Q2b, Q3 READY WITH FIXES (notes) |
| Sol | `SOL_RECHECK3_4645E0A.md` | rev 4 | Q1, Q2, Q2b, Q4 READY; Q3 NOT READY |
| Sol | `SOL_RECHECK4_D082318.md` | rev 5 | Q1, Q2, Q4 READY; Q2b (a), Q3 NOT READY |
| Sol | `SOL_RECHECK5_5C78B8F.md` | rev 6 | all READY |

Adjudications: `ADJUDICATION_37F20C8.md`, `ADJUDICATION_2DB4D63.md`, `ADJUDICATION_DBA31FB.md`, `ADJUDICATION_4645E0A.md`, `ADJUDICATION_D082318.md`. Nothing was left unrepaired. Fable did not re-check revisions 5 and 6, which only narrowed claims. No statistician reviewed any of this.

## Exchange (verbatim)

### Question 1

> "D-20, technical bindings (proposal §1–§3, §5): fix the existing statistics code to the exact engine version the calibration runs on; fix the screen, mapping and held-out runner to their frozen copies; adopt the exact random-draw rules for the two null tests (G-11, G-14); amend the seed-bytes wording to match the reviewed engine; and build the s_inputs check into the screen. Adopt?"

| Option | Description shown |
|---|---|
| "Adopt (Recommended)" | "All the technical rules in proposal rev 6 §1–§3 and §5 become your decision. Reviewers: Sol READY, Fable READY. Lockbox rows stay open." |
| "Keep blocked" | "Nothing is decided. The screen can't be built, so the freeze can't happen." |

**Answer:** **"Adopt (Recommended)"**

### Question 2

> "Model libraries (proposal §3a): C2 must run in the same image as the calibration, so this has to be decided before the full run starts. Which?"

| Option | Description shown |
|---|---|
| "(a) Add to image now (Recommended)" | "One reviewed PR adds scikit-learn and LightGBM to the calibration image and must prove the engine's outputs are byte-identical; then the re-pilot is re-run on the new image (more server time). Model-fitting strategies stay possible in C2." |
| "(b) No model strategies in C2" | "Image unchanged, no re-pilot. Every C2 strategy must be a pure rule; using models later needs a new image and a new qualification run." |

**Answer:** **"(a) Add to image now (Recommended)"**

### Question 3

> "Seed source for G-1, G-11 and G-14 in C2 (proposal §4): which seed feeds their random draws?"

| Option | Description shown |
|---|---|
| "(b) Beacon seed (Recommended)" | "Seed exists only after the public post, closing the free 'try cosmetic edits offline' loophole. Changes wording you decided earlier. You accept the stated assumption that a hashed seed acts as a fresh random draw. Retrying after the beacon stays possible, at the cost of one m each, with no probability bound claimed across retries." |
| "(a) Keep current seed" | "Wording unchanged. The seed is known before the post, so a declarer can search it offline for free (disclosed weakness)." |

**Answer:** **"(b) Beacon seed (Recommended)"**

### Question 4

> "D-13, what the CPCV diagnostic reports (proposal §6). It never feeds any pass/fail decision. No statistician has reviewed it. Which?"

| Option | Description shown |
|---|---|
| "(a) Both estimands (Recommended)" | "Median and 5th percentile over the 7 paths for E-IMPROV and E-DIFF, each labelled, with exact path and quantile rules. Binds the least." |
| "(b) One estimand" | "Simpler, but picks a winner without a reason." |
| "(c) Report nothing" | "Contradicts the frozen protocol text, which requires the report." |

**Answer:** **"(a) Both estimands (Recommended)"**

## Effect

1. **D-20 (rest), adopted as rev 6 §1–§3 and §5.** This covers:
   - the code bindings B1 (engine-commit files and object files, with the C2 checks);
   - the G-9 binding and M13, which supersedes the Annex B §2.4 stream-extension sentence;
   - B2, the R-7 and `seed_disclosure.derivation` named-object encoding;
   - the G-11 and G-14 stream rules B3 and B4, with the model-seed rules;
   - B6, the screen seeds, as a clarification of accepted prereg §7.2;
   - B5, the `s_inputs` mapping built in `calibration/screen.py`.

   Lockbox clauses and D-11/D-12 stay open. For G-1 this is matrix row option (b), reuse of the Task 12 stream. It is accepted on the condition that the Task 12 tests and the D-19 reference vectors pass at the bound commit on the pinned runtime.
2. **Model libraries, option (a).** Before the run definition is recorded:
   - one §16-reviewed image PR adds scikit-learn and LightGBM, with hash-pinned transitive dependencies, to the calibration image;
   - that PR must show byte-identical canary and reference-vector outputs on the rebuilt image;
   - the FE-7 re-pilot is then re-run on the rebuilt image, with the CPU probe and the resume test, before the go-ahead.

   FE-4's "image done" status reopens until that PR merges.
3. **C2 seed source, option (b).** G-1, G-11 and G-14 use the beacon-protected trial seed, `SHA256(cj({"family_seed": family_seed_f, "trial_id": <id>}))`.
   - This overrides l.266 for C-1, C-10 (3) and C-12 (5) only.
   - The owner accepts the stated modelling assumption: a SHA-256 seed acts as an unpredictable draw, independent of the data. Under it, the D-19 `U_G` rate transfers to the first attempt on a window declared before any outcome on it is seen.
   - No probability bound is asserted across outcome-dependent retries. The C-13 "Seeds" bullet is rewritten, not deleted.
4. **D-13, option (a).** CPCV reports the median and 5th percentile (`type_seven_quantile`) over the 7 XOR-assembled paths, for `E-IMPROV` and `E-DIFF`, each labelled. Nothing reads these outputs. The matrix's `STAT` acceptance is absent, and is recorded here as absent.

## Not changed by this decision

- No frozen file, and no `HUMAN_DECISION_MATRIX.md`, is edited. Nothing is activated.
- The S4 draft markers are replaced in a separate revision of the S4 draft, which follows this record.
- The image PR, the re-pilot re-run and the screen build are separate tasks, each with its own review and owner PR review.
- No calibration run, cycle, trial, data access, deployment or trading is authorized.
