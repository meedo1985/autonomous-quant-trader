# Sol High focused check of the broadened method design rev2 at `020c8d0` — NOT READY

Date: 2026-10-03. Focused check (rev 1 → 2 changes) by the OpenAI family for
R19-2; run in parallel with, and without sight of, `FABLE_REVIEW_020C8D0.md`.

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < <prompt>`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a100c9-3ab0-7312-9c89-5aa7b249d95f`;
  tokens used 98,181; exit 0. (Self-report names only "GPT-5"; the CLI header
  is the observed model metadata.)
- Prompt: `REVIEW_PROMPT_R2.md` (committed `74f300c`) with `{{PREFIX}}`
  replaced by `SB2` (substituted file SHA-256
  `566ebbbe41c3b0cd408b72973e53b169183f744d2597fb64aafcd56b7f41d681`).
- Findings: SB2-1 BLOCKER; SB2-2, SB2-3 NON-BLOCKING. Nothing is decided by
  this record; no finding is repaired here.

Below is the reviewer's final message, verbatim.

---

Model: **GPT-5, OpenAI Codex family**; exact deployment identifier is not exposed.  
Commit reviewed: `020c8d0515ac85b6d02a22dbd14a80e030008a8c`  
Verdict: **NOT READY**

### Revision-1 findings

- **SB1-1 — RESOLVED:** `S0` now uses recentred resamples and each `D_j` uses uncentred resamples.
- **SB1-2 — PARTLY:** stationarity, short memory, and variance limits are stated, but the supported-domain sentence still says finite variance while `D_j` requires a finite fourth moment.
- **SB1-3 — RESOLVED:** the conservative-largest claim and ineffective `T/4` rule were removed; the rule is labelled a calibrated heuristic.
- **SB1-4 — PARTLY:** family-level identity, stream extension, declaration checks, and development-selected `T_min` are addressed; exact seed encoding remains incomplete.
- **SB1-5 — RESOLVED:** the claim is explicitly per-cycle and disclaims lifetime and public-history protection.
- **SB1-6 — DEFERRED to the owner/amendment:** B-3 now clearly presents the changed numerical meaning of `D`.
- **SB1-7 — RESOLVED:** D-19 must rerun the exact 2,000-replicate inner procedure.
- **SB1-8 — DEFERRED to the owner:** B-5 presents reporting, alpha spending, and cycle caps with both accumulation bounds.
- **SB1-9 — DEFERRED to D-19:** the missing preregistration components are now enumerated but not yet specified.

- **FB1-1 — DEFERRED to D-19:** the false conservative claim is removed and `L/T` is a covariate, but the block selector still needs qualification.
- **FB1-2 — RESOLVED:** `D_j` and `z_j` are computed and checked for every column.
- **FB1-3 — DEFERRED to the owner/amendment:** the Constitution §9 conflict and required amendment are explicit.
- **FB1-4 — RESOLVED:** the dead `L > T/4` rule is replaced by `BLOCK_LENGTH_CAPPED`.
- **FB1-5 — PARTLY:** using `u` fixes the null-`S0` target, but it is not generally adequate for the new observed-law `D_j` target; see SB2-1.
- **FB1-6 — DEFERRED to D-19:** sparse columns are disclosed and required as calibration cells.
- **FB1-7 — RESOLVED:** eligibility is outside `U_proc`, and infrastructure causes take `U_ops` precedence.
- **FB1-8 — PARTLY:** a family seed is proposed and convention/vector changes acknowledged, but its exact canonical construction is unfinished.
- **FB1-9 — RESOLVED:** `fsum`, two-pass variance, replicate order, and rounding language are specified.
- **FB1-10 — RESOLVED:** the O18-2 basis, changed meaning of `D`, and cancellation of `T−1` are disclosed.
- **FB1-11 — DEFERRED to the owner:** presented as B-6.
- **FB1-12 — DEFERRED to the owner:** presented as B-5 rather than an implicit drafting choice.
- **FB1-13 — RESOLVED:** the two erroneous citations are corrected and the inherited citation is labelled.
- **FB1-14 — RESOLVED:** the bootstrap-p-value alternative no longer claims trivial calibration.
- **FB1-15 — DEFERRED to D-19:** the declaration-time non-monotonicity is disclosed and made a required cell.
- **FB1-16 — RESOLVED:** the missing calibration dimensions are now listed.
- **FB1-17 — RESOLVED:** calibration cost is quantified and assigned to the compute plan.

### Revision-2 findings

| ID | Severity | Location | Scenario and evidence | Proposed disposition |
|---|---|---|---|---|
| **SB2-1** | **BLOCKER** | `DESIGN.md` §2.2–2.3, lines 57–89 and 95–100 | One `L`, selected solely from null influence `u`, drives both null `S0` and uncentred `D_j`. At nonzero Sharpe, the influence for `D_j` is `ψ=u−(S/2)(u²−1)`; volatility dependence can exist in `u²` while `u` is nearly uncorrelated. A deterministic 365-point variance-regime construction gave the existing selector `L(u)=1` but `L(ψ)=15.762` at `S=1.124`. Thus `D_j` can be underestimated inside the stated stationary, short-memory, finite-fourth-moment domain. Sharing index sequences does not repair a target-mismatched block length. | Define and preregister either separate null/observed-law block selectors and streams, or a joint selector targeting both every `u_j` and every observed-law `ψ_j`. Add conditional-heteroskedastic/volatility-dependence cells and freeze only a candidate that passes held-out qualification. This blocks B-3 and the per-nominee branch of B-6. |
| **SB2-2** | **NON-BLOCKING** | §2.4, lines 108–115 | The family-seed prose does not define canonical bytes/domain separation or the precise mapping into `ReplicateStream`. The existing seed material separately includes convention hash, purpose, asset, cost, window, output length, and replicate index; the proposal also places the purpose inside the family seed, creating an unresolved once-versus-twice ambiguity. The declared seed fields omit the cited data-manifest identity. | Freeze an exact compact serialization and domain tag; bind the complete hashed declaration/data manifest, convention hash, stream fields, and purpose exactly once; regenerate reference vectors. |
| **SB2-3** | **NON-BLOCKING** | §2.5, lines 117–129 | The section says “in order,” lists `T<T_min` first, then says declaration validity “precedes everything below.” P18-1 instead makes an invalid declaration prevent the cycle from starting. The `U_ops`/`U_proc` cause-first split itself is correct. | State one total precedence: declaration validity, window eligibility/`T_min`, then computed reason codes; retain infrastructure-first classification for computed symptoms such as missing data. |

Using the same index sequences for recentred `S0` and uncentred `D_j` is otherwise acceptable and preserves their finite-`B` dependence for nested calibration. Computing `D_j`/`z_j` for every column is correct. `BLOCK_LENGTH_CAPPED` is implementable because the existing result exposes raw length and upper clipping, but its support boundary still requires D-19 certification.

Local review gate: **BLOCKED by SB2-1**. Tests, lint, type checks, and frozen-file verification were not applicable to this read-only design review; no files changed. No network, confirmation/lockbox data, or other revision-2 review was accessed.

### Owner summary

The revised design fixes most of the first-round problems.  
Using centred data for the hurdle and uncentred data for uncertainty is sensible.  
The remaining blocker is that both calculations still use a block length chosen for only the centred calculation.  
That can miss volatility clustering and make a strategy appear more certain than it is.  
Do not decide B-3 or the per-strategy B-6 route until that selector is redesigned and checked.