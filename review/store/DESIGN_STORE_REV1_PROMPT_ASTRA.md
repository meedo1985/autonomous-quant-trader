# Astra review prompt: store build design rev 1

You are an independent adversarial design reviewer (read-only). Repository root is the
current directory, branch `store-design`, at the commit that adds this prompt. Do not modify
any file. Your findings are proposals; you are not an authority. The builder was Claude
Opus 5.5. The store is §16 lockbox ACL tooling and protocol-enforcement logic.

Read: `review/store/DESIGN_STORE.md` (rev 1, the subject). Authority (read with
`git show 3abcafb:<path>`): `review/governance-statistics-amendment/s4-amendment-draft/ANNEX_D_LOCKBOX.md`
(§D-2.3..§D-2.8, §D-3.6..§D-3.9), and for crash rows and tests
`review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV8.md` and
`OPTION_C_PROPOSAL_REV2.md`..`_REV5.md`. Module obligations: `calibration/c2_lockbox.py`
`Store`/`ReadSession` (about l.1210-1262), `calibration/c2_confirmation.py` `Store`/`Persist`
(end of file), `review/r14a-modules/DESIGN_SLICE6B.md` §12. Existing code:
`src/aqt/core/ledger.py`, `src/aqt/core/attempts.py`, `pyproject.toml` import-linter
contracts. Constitution `docs/RESEARCH_CONSTITUTION.md` §7, §16, §26, §28. Do not reopen
Annex D's decided rules or owner decisions; check the design against them.

Check:
1. Coverage: every store obligation in Annex D §D-3.6..§D-3.8, §D-2.4..§D-2.8 (the
   store's part), the two modules' `Store` docstrings and 6b §12 has a home in §4 and a
   test in §5, or is correctly assigned to another build (publisher, signer, owner command,
   access tooling). List anything missing or misassigned.
2. Soundness of the [DESIGN] choices: D-1 (two ledgers), D-2 (package `aqt.store`, no
   import of `calibration`, shared constants with equality tests), D-3 (own index writer
   byte-identical to `append_entry`; `scan_bytes`), D-4 (file layer, `CrashFs` outcome
   model, clock), D-5 (persisted §26 stop marker), D-6 (Unix socket, `SO_PEERCRED`,
   role argument in the core). Any that contradicts Annex D, the modules, or makes a crash
   row or test impossible?
3. The durable-before-use order, `L_store` scope (who may and may not hold it), and the time
   rule: does the design state them as Annex D does?
4. Slicing (§6): order and dependencies; can each slice be reviewed alone?
5. Owner/S4 items (§7): missing, or wrongly claimed as decided? Is ST-O-5's reading of C
   (written at the look) right?

Output (Markdown, concise): verdict ACCEPT / ACCEPT WITH NOTES / FIX; model ID you can
observe; files and line ranges read; findings ST1-A-1.. with severity, location, evidence,
failure scenario, proposed correction.
