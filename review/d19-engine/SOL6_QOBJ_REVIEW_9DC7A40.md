<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-12. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a130a2-fe94-7fc2-84cd-35c6d0ffa4f8. Tokens used: 39,629. Made from a packet built from commit 9dc7a40: the prompt below, preregistration §4 and §13 item 6 excerpts, the S16-2/S16-4 and BO-3/BO-4 rows, git diff 1138eef 9dc7a40, d19_choose main, rundef run_plan and start_gate, chunks.py and reduce.py. -->

> # Review: D-19 qualification-object builder (commit 9dc7a40, branch d19-qobj)
> 
> You are an independent adversarial reviewer working read-only, not an authority. Everything is attached. Check `calibration/qobj.py` against preregistration §4 (contents, `qualification_object_sha256`), §13 rev 7g item 6 (the object carries the run definition's runtime values unchanged, every chain's final head, the reduced results), the S16-2 and S16-4 obligations, and the build-order conditions BO-3 and BO-4. Look for: a §4 content item missing or represented by something weaker; any way a builder output could differ from what the complete chains and fixed rules give; any refusal that could be bypassed or that writes partial output; anything that would break at a real freeze (for example the start gate, the two checkouts, the run plan); and whether the tests would catch a broken implementation. The mapping (§3.6), screen (§7.2) and held-out runner are not built yet; the builder refuses while their files are missing. Verdict ACCEPT or FIX; findings get stable IDs QO-n with severity, file:line and a concrete failure scenario.
> 

## Review (final message, verbatim)

## Verdict: FIX

The builder cannot produce a qualification object at this head. Several checks also need repair before opening the qualification gate.

- **QO-1 — Blocker — [calibration/qobj.py:161](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/qobj.py:161>).** `build()` calls `rundef.run_plan()` for a qualification manifest, but the supplied `run_plan()` always raises for that purpose. A real freeze therefore fails even after the missing mapping, screen, and runner are built. [The tests](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_calibration_qobj.py:105>) replace `run_plan`, so they cannot catch this.

- **QO-2 — High — [calibration/qobj.py:67](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/qobj.py:67>).** The S16-2 check compares Git’s caller-controlled committer timestamp with a caller-supplied `threshold_started`; it does not establish when the first threshold chunk was written or that the commit was pushed. A definition committed after the first chunk can pass if the supplied start time is later. The freeze needs auditable first-chunk and commit evidence.

- **QO-3 — High — [calibration/qobj.py:158](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/qobj.py:158>).** The builder copies engine files from `run_root` and runs `choose` there, but derives `alpha_s` and `cell_thresholds.json` using modules imported by the builder’s own checkout. If those checkouts differ, the object can contain the pinned generator and choices alongside a different `alpha_s` or per-cell thresholds. Those derived values need to come from the pinned engine, or be checked against it.

- **QO-4 — Medium — [calibration/qobj.py:198](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/qobj.py:198>).** §4 content coverage is not established. The file set explicitly saves per-cell threshold statistics only for *qualifying* units, and the builder does not check that `choices.json` contains an enumerated-test manifest or exact-binomial outputs. A report without those items passes the supplied success test. Make each required item explicit and test its presence and provenance.

- **QO-5 — Medium — [calibration/qobj.py:136](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/qobj.py:136>).** File existence is the only BO-4 check for mapping and screen; there is no evidence check for their §16 reviews, the screen’s seven prescribed gates, or held-out-runner review. After QO-1 is repaired, placeholder files like those used by the tests could satisfy this check. The freeze procedure needs a verifiable BO-4 gate before the hash is posted.

- **QO-6 — Medium — [calibration/qobj.py:168](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/qobj.py:168>).** Chain-head comparison, host-list hashing, and threshold reduction make separate reads without a snapshot or final head check. A complete chain replaced between those reads can yield `cell_thresholds.json` or an S16-4 host hash from different bytes than the head in `choices.json`. Freeze immutable chain bytes or recheck all heads after reduction.

- **QO-7 — Medium — [calibration/qobj.py:206](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/qobj.py:206>).** Output is written directly into `out`. A disk or write error after the first file leaves a partial object, contrary to the stated “writing nothing” refusal property. Stage and verify the whole directory before publishing it.

This is a read-only review of the supplied material. The local command runner failed before starting a shell, so I could not run tests, inspect the checkout, or commit the review record required by the project instructions.