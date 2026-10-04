# Sol re-review DS3 of the D-19 preregistration rev 3 at `59f5f6c`: UNSOUND

Date: 2026-10-04. This is an R19-2 independent statistical re-review by the different model family. The prompt was the same as Fable DF3's, with the ID prefix `DS3`.

Command: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high`. The CLI header records `model: gpt-5.6-sol`, `reasoning effort: high` and session `01a106f9-0bcc-7ed2-8a77-1248a4a432f6`. The final message is reproduced below unchanged.

---

Model: OpenAI Codex, GPT-5 family; exact served model identifier is not exposed  
Commit: `59f5f6c38553caf907f551827d0dd21796a82bc9`  
Verdict: **UNSOUND**

Two blockers remain: nonconformance with decided O18-4 and an unspecified/unapproved `AQTQ1` commitment channel.

### DF2/DS2 status

| Finding | Status | Reason |
|---|---|---|
| DF2-1 | RESOLVED | Both attempts use `0.025/M`; targets recomputed correctly. |
| DF2-2 | PARTIAL | Large separate threshold run and tails added; qualification ordering remains circular (DS3-3). |
| DF2-3 | PARTIAL | Dependence cases named, but K=2 is omitted and generators remain incomplete. |
| DF2-4 | PARTIAL | Declared K is restricted, but the restriction contradicts O18-4’s required two-trial cell. |
| DF2-5 | RESOLVED | U-1 explicitly authorizes the narrower `U_proc^R` proposal. |
| DF2-6 | PARTIAL | Hourly production-count screen added; complete bar construction and data lineage remain unbound. |
| DF2-7 | PARTIAL | Hash-plus-drand design is sound; `AQTQ1` is not covered by decided O-6a. |
| DF2-8 | RESOLVED | All cells receive 22,000 development replications and use 90% UCBs. |
| DF2-9 | RESOLVED | Q1–Q4 are common-law tests; Q5 is family-labelled; `M` comes from the manifest. |
| DF2-10 | RESOLVED | Scale, Q5 side effects and invalid-equity treatment corrected. |
| DF2-11 | RESOLVED | Canonical JSON seed objects are specified. |
| DF2-12 | RESOLVED | Integrity boundary, wrong-`g` consequence and cap rule specified. |
| DS2-1 | RESOLVED | Attempt-level confidence allocation is coherent. |
| DS2-2 | RESOLVED | §1 and §11 now claim only `U_proc^R`, consistently with U-1. |
| DS2-3 | PARTIAL | Production settings fixed; screen inputs/reproducibility remain incomplete. |
| DS2-4 | PARTIAL | Diagnostics and tails improved; classifier still conflicts with O18-4 and threshold ordering. |
| DS2-5 | RESOLVED | No unsafe conditional development stage remains. |
| DS2-6 | RESOLVED | Family/test counting is conceptually reconciled. |
| DS2-7 | RESOLVED | All three G-12 horizons are evaluated. |
| DS2-8 | PARTIAL | Several choices fixed, but dependence generators and data/runtime bindings remain incomplete. |

### Main designs

| Design | Assessment |
|---|---|
| Real-window classifier | **Not yet sound as the required support classifier.** It is a reasonable fail-closed sample diagnostic, with refusal correctly counted in `U_proc^R`, but it neither maps a declared design to a qualifying cell nor runs before declaration as O18-4 requires. The text uses the **99.999th percentile** (`0.99999`), then takes an extreme across cells—not a retained per-cell 99.99th-percentile rule. |
| Q5 sign-flip null | **Sound for the claimed first-moment null.** Independent symmetric block signs give conditional `E[X_j,t]=0`; initialization and side effects are disclosed. |
| Route S | **Honest and acceptable in principle.** U-1 explicitly permits an amendment to replace full P18-7 coverage with calibrated `U_proc^R` plus an uncalibrated fail-closed screen. It remains weaker, requires formal amendment activation, and presently has execution/lineage gaps. |
| Exact-binomial development | **Sound core construction.** Independent arithmetic reproduced τ values `0.0176780`, `0.00112569`, and `0.000414833`. The 22,000-all-cells development removes DS2-5. The reported “joint pass probability” remains underdefined. |
| Leg generators | **Not fully sound/reproducible.** The GARCH fourth-moment check passes (`0.9825 < 1`), but several cross-column generators cannot yet be instantiated uniquely. |
| Qualification-bound seeds | **Sound cryptographic idea, incomplete governance implementation.** Hashing the qualification object and adding post-commitment drand entropy prevents grinding only if the commitment channel is valid and uniquely specified. `AQTQ1` currently is not. |

### New findings

| ID | Severity | Location | Problem | Evidence | Fix |
|---|---|---|---|---|---|
| DS3-1 | BLOCKER | §3.2, §3.5; D-18 O18-4 | The revision contradicts a decided calibration requirement. O18-4 requires two-trial families and a deterministic pre-declaration design-to-cell mapping. Rev 3 permits only K `{1,5,20,80}` and classifies observed `X` after Annex B rules 1–4. | O18-4 lines 420–427 versus preregistration §§3.2/3.5. Passing is expressly only a minimum condition, so no qualifying cell is identified for a real declaration. | Add K=2 qualifying cells and a deterministic declaration-time design-to-cell mapping; retain the sample classifier as a separate refusal check. Alternatively obtain an explicit owner decision and amendment replacing O18-4, with the weaker certification stated. |
| DS3-2 | BLOCKER | §§4, 8; O-6a SPEC/decision | `AQTQ1` on dedicated key `A_Q` is not an adaptation already supplied by O-6a. The decided channel fixes an `AQTC2` payload containing `declaration_sha256`, plus specific address, bound coin, deadline and first-post rules. | O-6a SPEC §3 and OWNER_DECISION_O6A; preregistration lines 195–196 and 304 invent a different prefix/key without its corresponding specification or owner decision. Without a valid pre-beacon commitment, qualification-object grinding remains possible. | Specify, review and owner-decide a separate qualification-object channel, including exact payload, address/outpoint/deadline, first-post and failure rules—or formally extend O-6a before certification. |
| DS3-3 | MAJOR | §§3.2, 3.5, 4 | Threshold construction uses “qualifying cells” before qualification is known. | A cell becomes qualifying from its development cap rate (§3.2), but the threshold run occurs before development (§§3.5, 4). | Run all enumerated candidate-grid cells and freeze the extreme over all of them, or explicitly retain all per-cell outputs and define the post-development selection rule. |
| DS3-4 | MAJOR | §2 step 5; §§6–7; Annex C C-9 | The claimed `U_proc^R` bound lacks an exact combined event, and G-10 is incorrectly described as being evaluated “on the nominee.” | Annex C requires every trial to have Sharpe on every PBO half. Bounding each “other gate” separately would not imply their combined `0.0015` allocation. | Define one event `U_G = G1 unavailable ∪ G2 unavailable ∪ G10 unavailable ∪ any-H G12 unavailable`, apply one CP test to it, and specify G-10 evaluation over the full family matrix. |
| DS3-5 | MAJOR | §§3.1–3.2, 4, 7.2 | Generators and screen inputs remain non-executable or non-reproducible in places. | “Half” and cluster sizes `K/4,3K/4` are undefined for K=5; factor/copula constructions are absent. The screen rebuilds prices and volume but does not specify complete OHLC/feature inputs. The qualification object does not list the exploration-data manifest/hash. | Freeze integer grouping and exact covariance/copula formulas, complete bar reconstruction and failure rules; bind exploration-data, classifier, screen, runtime and dependency hashes into the qualification object. |
| DS3-6 | MINOR | §5 item 4 | Marginal 90% UCBs do not by themselves define a “joint pass probability.” | Coverage is not simultaneous across hundreds of development cells, and dependence between tests is unspecified. | Report a clearly labelled plug-in diagnostic or a Bonferroni lower bound; do not present it as a confidence-certified joint probability. |

### Remaining overstatement

Read literally as a statement only about enumerated synthetic cells, §1 is substantially repaired. It still cannot support an operational C2 qualification claim until DS3-1 supplies the design-to-cell bridge, DS3-2 makes held-out commitment non-gameable, and DS3-4 defines the exact union event being bounded. It correctly makes no certified rate claim for screened gates.

### Commands run

- `rtk git status --short --branch --untracked-files=no`, `rev-parse`, `branch`, `show`, `ls-tree`, `diff --check`.
- Read-only `git show`/`rg` inspection of the named records, Annexes A–C, Constitution, protocol, hash specification, D-18/O18-4 and O-6a records.
- In-memory standard-library Python: exact binomial/CP thresholds, screen power, GARCH fourth moment, classifier order-statistic arithmetic and manifest-count arithmetic.
- Initial SciPy arithmetic attempt failed with `ModuleNotFoundError`; the standard-library calculation succeeded.
- Tests/lint/type checks: N/A for a document-only read-only review.
- No network, edits, commits, pushes, or restricted-data access. Untracked files were not enumerated. This review is not a committed repository review record.

Revision 3 fixes the alpha budget and honestly narrows the 1% no-result claim under U-1.
It is not ready because the decided K=2/design-mapping rule is missing and the AQTQ1 commitment channel is not validly specified.
Do not accept or run certification until those blockers and the execution/reproducibility fixes are closed.
