# Sol review DS7 of the D-19 preregistration rev 7 (§13 computational equivalence) at `af03d00`: UNSOUND

Date: 2026-10-04. This is an R19-2 independent review by the different model family. A parallel Fable review was stopped by a Claude usage limit (HTTP 429) before it produced any output; no Fable record exists for rev 7.

Command: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high`. The CLI header records `model: gpt-5.6-sol`, `reasoning effort: high` and session `01a1072c-042d-7c81-a547-17730ab161a9`. The final message is reproduced below unchanged, except that one local link was shortened to its repository-relative form.

---

Model: OpenAI Codex, GPT-5 family; exact serving-model identifier was not exposed  
Commit: `af03d00d549bdc7f468e42bffe0af81c1d458e0a`  
Verdict: **UNSOUND**

1. As written, `F` cannot certify the claim about `R`. The audit can detect some defects, but it neither proves event equivalence nor bounds undetected disagreement tightly enough.
2. Keeping production on `R` and treating a held-out mismatch as a burned failed attempt are consistent with P18-6 and Annex B. The development namespaces and threshold-run provenance are not fully consistent.
3. The public audit selector, unsupported `1e-9` band, omitted decision boundaries, and unrestricted development reruns provide defect or gaming routes.

### Findings

**DS7-1 — BLOCKER — [PREREGISTRATION.md §13.2–§13.4](review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md)**  
Problem: A 1% audit does not establish that the remaining 99% of `F` event labels equal `R`.  
Evidence: At `N=20,000`, approximately 200 replications are audited. Zero mismatches gives only about a 1.49% one-sided 95% upper bound on the mismatch rate. If 20 labels differ—a 0.1% rate capable of changing a near-boundary certification—the 1% audit misses every mismatch with approximately 81.8% probability. The `1e-9` band has no forward-error proof.  
Fix: Either compute every certification event with `R`, or provide a verified numerical-error bound and recompute every replication within that bound of every decision boundary. Alternatively, incorporate a simultaneous mismatch-rate bound conservatively into every certification bound; 1% is insufficient for that route.

**DS7-2 — BLOCKER — §13.1–§13.3; §3.5; §5**  
Problem: Near-threshold recomputation covers only `z_crit` and `1.96`, while permitted fast operations can change non-`z` events. The threshold phase is not audited.  
Evidence: Fast evaluation can disagree on `INVALID_REPLICATE`/`INVALID_ARITHMETIC` through cancellation in variance calculations, PW cap/failure, classifier acceptance through `L/T`, G-1 availability, or index sequences. None necessarily produces an `F` value near a `z` boundary. The million-replication threshold run uses PW-derived diagnostics but §13 names only development and held-out audits. Also, `z_crit` is selected after the stored `F` values, without a specified recompute-and-reselect fixed point.  
Fix: Protect every discrete boundary, run the threshold statistics through `R` or prove their exact equivalence, and specify an iterative procedure that recomputes and reselects `z_crit` until stable.

**DS7-3 — BLOCKER — §13.3–§13.4 versus §8 and §4**  
Problem: The development audit set is predictable, and repair reruns are not completely bound.  
Evidence: The audit key omits `ns`; the development anchor is already known, so audited replication numbers are enumerable and repeat across new development namespaces. Section 8 defines only `d19-dev-v1`, while §13 requires an unspecified new namespace. An engine repair discovered after the threshold run does not explicitly require rerunning affected threshold work.  
Fix: Define deterministic versioned development namespaces, include namespace and engine hash in the audit key, preserve all failed runs, and rerun every affected earlier phase. For meaningful anti-gaming, commit all `F` outputs before revealing an independent audit salt.

Checks were read-only and commit-scoped. No network, `data/` contents, confirmation/lockbox data, edits, tests, or pushes were used. Tests/lint are N/A for this document review. Local gate: **BLOCKED**. Per repository policy, this review must be committed before it can be cited as completed R19-2.

### Owner summary

The real cycle would still use the exact calculation, which is correct.  
But checking only 1% cannot prove that the fast calibration made the same decisions; important rare errors would usually be missed.  
Do not accept revision 7 until every decision boundary, threshold phase, and rerun namespace is fully protected.
