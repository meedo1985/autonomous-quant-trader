# Sol review BS2 of the D-19 preregistration §13 rev 7c at `09b0fb9`: UNSOUND

Date: 2026-10-04. R19-2 independent statistical narrow re-review, run with Codex CLI (`codex exec`, model requested `gpt-5.6-sol`, reasoning effort high), read-only. The drafter is Claude Opus 5.5. The reviewer's final report is reproduced below unchanged.

---

**Model identity:** OpenAI Codex, GPT-5 family; no finer serving-model identifier is exposed in this session.  
**Commit reviewed:** `09b0fb92a8b1169c0a1436d63839b412c8f3901c` on `docs/d19-recommendation`  
**Verdict:** **UNSOUND**

Not every BF1/BS1 finding is resolved. The numerical repairs are correct, but BF1-5/BS1-5 remains incomplete.

### Findings

- **BS2-1 — BLOCKER — [§13 item 6 / §4 freeze order](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md:504>)**
  - **Problem:** Threshold and development chunks must record `qualification_object_sha256`, but that hash is created only after threshold and development finish.
  - **Evidence:** The qualification object contains threshold statistics, final thresholds, development-selected values and outputs; §4 hashes it after development. The checkpoint rule is therefore circular or requires post-hoc mutation. The chain also leaves its final chunk unbound unless a final head hash is recorded.
  - **Fix:** Bind threshold/development chunks to a pre-run definition hash available before execution; include their final chain heads and results in the qualification object; bind held-out chunks to the resulting qualification-object hash. Record each chunk’s own content hash and the final head.

- **BS2-2 — MAJOR — [§13 item 3](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md:477>)**
  - **Problem:** Availability-based demotion is statistically valid, but its override is internally ambiguous. Accepted §1 defines challenge cells only through the cap rule, §3.3 lists only cap-demoted cells, and §13 says §1 remains unchanged except for `K` and `T`.
  - **Evidence:** These alternatives produce different qualifying support and potentially different certification outcomes.
  - **Fix:** Explicitly override §§1, 3.2 and 3.3; add availability-demoted cells to the challenge definition; correct the “Unchanged” list. Once fixed, independent held-out certification removes any selection effect from development-based demotion.

- **BS2-3 — MAJOR — [§13 item 2 versus §12](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md:467>)**
  - **Problem:** `T = T_C2` conflicts with decided A-B7’s `T ≥ T_min`, and dropping unequal-`T` coverage changes O18-4. The correct owner questions are present, but §12 still says acceptance requires only `Q-1`; §13 does not name §12 as overridden.
  - **Fix:** Override §12 explicitly and require affirmative, separately recorded answers to `O18-4-T` and `A-B7-EQ`. Until then, the equality rule is only a proposal.

- **BS2-4 — MAJOR, pre-run — [runtime and host migration](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md:502>)**
  - **Problem:** “The check catches any change” is too strong. The decided runtime identity hashes Python/NumPy/OpenBLAS and records OS/architecture and CPU feature flags, but not system libraries, CPU model or microcode. A security update or host migration can therefore pass identity and one canary while changing another numerical path.
  - **Fix:** Freeze the complete runtime image and relevant host identity, prohibit updates during a run, and execute the full frozen reference-vector suite on every start/resume. Define treatment of chunks after any host change.

- **BS2-5 — MINOR — [§13 item 4](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md:491>)**
  - **Problem:** `4/300001` is exact for continuous diagnostics. With inclusive ties and discrete diagnostics such as zero-day share, the marginal expected exceedance is **at most** that value, generally smaller.
  - **Fix:** Say “marginal expectation ≤ `4/300001`, with equality for continuous diagnostics”; the eight-tail total is correspondingly ≤ `1.0667×10⁻⁴`.

### Checks that passed

The 12,000-development UCBs reproduce as `1.91864×10⁻⁴` for zero events and `3.24104×10⁻⁴` for one. The 20,000-replication τ values, ranks 299,997/4, eight-tail arithmetic, and inclusive ties are otherwise correct. The 2,000-replication runs are legitimately report-only.

The estimate arithmetic is correct: `104×32,000×4.5s = 4,160` core-hours; adding 300 and multiplying by 1.2 gives `5,352 ≈ 5,400` server-core-hours, or about 3.66 ideal months on two continuously available vCPUs. It is properly labelled unmeasured.

No additional conflict found with P18-1–P18-7, A-U1/A-V1 or U-1 beyond the findings above. `git diff --check` passed. No network, confirmation/lockbox data, or `data/` contents were accessed. Tests, lint, typing and import checks are N/A for this read-only document review. This response is not yet the committed review record required by repository policy.

Most numerical repairs are correct, including the replication counts, tail ranks and server-time arithmetic.  
Do not accept rev 7c yet: its pre-freeze checkpoints require a hash that cannot exist until those runs finish.  
Define the pre-freeze hash, make the demotion overrides explicit, and record both owner decisions before re-review.
