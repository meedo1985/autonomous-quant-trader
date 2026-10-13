# Adjudication of the Fable and Sol narrow re-checks of the D-20/D-13 proposal rev 3 (dba31fb)

Records: `FABLE_RECHECK2_DBA31FB.md` (claude-fable-5-1),
`SOL_RECHECK2_DBA31FB.md` (gpt-6-sol). Adjudicated by Claude Opus 5.5, the
drafter. Revision 4 applies every disposition below.

| ID | Severity | Decision | Reasoning and evidence | Disposition in rev 4 |
|---|---|---|---|---|
| DF3-R1 / DC3-R1 | blocking | AGREE | Requiring every module to equal the engine commit, and object files also to equal the object, cannot both hold for an object file. `heldout.py` is a `scripts/` entry point, outside "modules". "Written after the run started" was wrong: `mapping.py` and the runner predate any full run. | §1 "Two bindings": two disjoint checks. Non-object modules are checked against the engine commit. Object files (`mapping.py`, `screen.py`, `heldout.py`, as module or entry point) are checked against the verified object copy, which replaces the engine entry as in `check_engine`. Re-labelled "object files (LATER), reviewed separately and frozen at the freeze". Q1 names the object-bytes binding. |
| DC3-R2 / DF3-R2 / DF3-R3 | blocking / note / note | AGREE | The separate model-runtime identity had no mechanism. The image digest already gates every byte. SciPy's OpenBLAS enters `runtime_identity`. "Numbers unchanged" was an untested claim. The image PR needs transitive pins, `libgomp1` and a NumPy-2.5.3 resolution. | §3a (a): the libraries are bound through the image digest, with no new identity and no engine-code change; the gating-identity change is stated. The image PR must show byte-identical canary and reference-vector outputs on the rebuilt image, is done before the run definition, and carries no qualification over from the old image. Transitive pins, the NumPy resolution and system libraries are listed. |
| DC3-R3 | blocking | PARTIAL | Holds: outcome-dependent retries mean a retained cycle is not one fresh draw, so the `U_G` claim must say what it covers. Contested in part: (i) `U_G` bounds unavailability, a no-result outcome, so selecting to escape it can only lower the retained cycles' unavailability; (ii) for the promotion claim, retries are corrected, not only priced, because every attempt increments `m` and the allowances sum below 0.10 (Constitution v1.1 §9). Rev 3, and DC2-R5's disposition, wrongly called `m` "a price, not a correction" for that claim. | §4: the `U_G` claim is per attempt, fixed before its beacon, not per retained cycle (with the `2p − p²` example). Selection against unavailability is conservative for `U_G`. Pass-seeking retries on G-1, G-11 and G-14 have no certified rate. Promotion retries are bounded by the allowance rule. The retry paragraph is corrected to match. |
| DF3-R4 | note | AGREE | The proposal must not record the owner's acceptance in advance. | §4: "Adopting (b) records the owner's acceptance of this assumption. If the owner does not accept it, neither option transfers the rate." |
| DC3-R4 | blocking | AGREE | Rev 3's rank rule does not keep a split's two test groups in one path. Checked: split {0,2} is the second split testing group 0 but the first testing group 2. | §6: path `p = 1 … 7` is the four splits `{g, g XOR p}`. Checked by enumeration: 28 distinct splits, each used once; every path covers groups 0–7 once. The rank rule is withdrawn. |
| DF3-R5 | note | AGREE | A path-dependent strategy's group returns depend on its starting state, and the benchmark was unstated. | §6: each test group starts flat at its first 00:00 UTC decision (exposure 0, no pending order, unset clock, fresh overlay state); the benchmark is the window's series, sliced by group. |

**Correction to an earlier disposition.** The rev 2 adjudication (DC2-R5) and
rev 3 called the `m` increment "a price, not a statistical correction". For
the false-promotion claim, that is wrong: the halving allowance is a
correction across attempts. It is only a price for the seed-driven gates,
which have no calibrated rate. Rev 4 states both.

Nothing was left unrepaired.
