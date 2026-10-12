# Sol High review of the D-06/D-07 proposal rev1 at `abcc2c9` — SOUND WITH FIXES

Date: 2026-10-03. The OpenAI-family review for R19-2. It ran in parallel with the Fable review and without sight of it.

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < <prompt>`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a10222-334d-74f0-9829-9ba09819e985`;
  tokens used 88,409; exit 0. (The reviewer's self-report names only "GPT-5 family"; the CLI
  header is the observed model metadata.)
- Prompt: `REVIEW_PROMPT_R1.md` (committed `abcc2c9`) with `{{PREFIX}}` = `SF1`
  (substituted file SHA-256 `49f8da2f268edbcce1784c34cc9bbbc7138735f7719270966bf4d726c2f800ad`).
- The reviewer's final message, verbatim:

---

Model: Codex, GPT-5 family; exact serving-model identifier is not exposed.  
Commit reviewed: `abcc2c9a58e59a1c91b4eae196a2dc30ac0aefb0`  
Verdict: **SOUND WITH FIXES**

Rule-by-rule: P6-1 and P7-3 faithfully apply existing conventions; P6-3 and P6-4 are compatible completions of missing frozen detail. P6-2’s anchor is compatible, but its month arithmetic is not. P6-5 adds a new availability condition. P7-1 and P7-2 are substantive statistical bindings—not meanings already fixed by the frozen text.

| ID | Severity | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| SF1-1 | BLOCKER | P6-2, P6-3 | With `s = 2023-01-31`, the proposed three-month boundary is May 1, so `[Jan 31, May 1)` includes April 30 and exceeds the ordinary clipped three-month interval ending April 30. The draft’s inclusive `23:59:59Z` window end also does not directly compose with half-open block intervals. | Frozen text fixes “3 months” but not arithmetic. First-day anchoring is supported by the sole-final-partial rule; roll-forward arithmetic is not. | Keep first-eligible-day anchoring, but define `B_k` independently from `s` using an explicit calendar-month convention—preferably target-month end clipping—with boundaries at `00:00 UTC`. Convert the eligible window to `[s,e)` where `e` is the first excluded UTC day. |
| SF1-2 | BLOCKER | P6-5; C-3 | A window with one to three complete blocks is computable under the frozen fraction but becomes `UNAVAILABLE` under `B_min = 4`. P7-1 can also reverse wins relative to `E-DIFF`, while P7-2 supplies a previously absent tie rule. | The matrix describes D-06/D-07 as open. Only P7-3 directly restates lines 280–282. | Replace C-3’s “not a change of meaning” claim. Describe the anchor, `B_min`, estimand, tie rule, and undefined-statistic handling as explicit candidate bindings; P6-5 is an additional eligibility/availability restriction. |
| SF1-3 | BLOCKER | P6-5 | `B_min` is delegated to D-19, although the amendment draft requires D-06/D-07 availability rules to be fixed before D-19 is preregistered and calibrated. The default of four has no supplied statistical rationale. | Draft §6 orders gate-availability decisions before D-19; M5 requires the fold minimum rules before the estimand matters. | Resolve `B_min` within D-06, with a rationale, or remove it and let the later frozen `T_min` govern window length. Do not leave D-06 dependent on D-19. |
| SF1-4 | BLOCKER | P6-4, P7-2, C-1 | One invalid block makes the entire gate unavailable. With 13 blocks, even independent per-block invalidity of only 0.07728% produces 1% gate unavailability, before accounting for other gates or the second family. | Constitution §6 and Task-12 support `UNAVAILABLE` for missing, irregular, nonfinite, or misaligned data. P18-7 places every technically invalid pre-lockbox gate inside the whole-cycle `U_proc ≤ 0.01` target. | Retain `UNAVAILABLE` for data-integrity failures. For otherwise valid zero-variance blocks, consider an explicit block-level non-win instead; this preserves the denominator, is promotion-conservative, and avoids consuming `U_proc`. If zero variance remains unavailable, D-19 must certify—not merely measure—the complete whole-cycle bound. |
| SF1-5 | NON-BLOCKING | C-1, C-2 | A fixed exposure tracking a variable benchmark is generally not zero-variance. Also, “no edge” alone does not imply a 0.5 block-win probability: the legs need an exchangeability or equivalent symmetry condition. Serial dependence is a separate assumption. The asserted 28-day embargo cap is not present in draft §2.1. | Exactly, `P[Binomial(13,0.5) ≥ 8] = 2380/8192 = 0.29052734375`. The numerical 29% is correct only conditional on `n=13`, `p=0.5`, and independent block outcomes. | Use cash/constant-return behavior as the zero-variance example. Label 29% as an illustrative exchangeable-independent calculation. Derive the actual block count from the declared embargo rather than asserting a 28-day cap. |
| SF1-6 | BLOCKER | §5 owner question | The question omits the month convention, `B_min`, exact-zero treatment, zero-variance treatment, and their `U_proc` consequence. “Accept or keep blocked” also omits the matrix’s revise and reject responses. | These omitted choices can alter availability or pass/fail outcomes and are central to D-06/D-07. | Present all material bindings and consequences, then offer accept, revise, reject, or defer. Explicitly state that valid zero variance must be chosen as either non-win or unavailable, and that unavailable outcomes count toward the whole-cycle 1% target. |

The proposal has a workable core: start blocks at the first eligible UTC day and count only complete three-month blocks.  
Its unusual month rule must be replaced or explicitly justified because it can make a block longer than three calendar months.  
The minimum-block rule cannot be deferred to D-19, because D-19 needs the final availability rules first.  
Missing data may properly make the gate unavailable, but valid zero variance is better considered as an explicit non-win to protect the 1% availability budget.  
The owner question must disclose all these choices and allow acceptance, revision, rejection, or deferral.