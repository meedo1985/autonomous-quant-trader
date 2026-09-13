# Task 7 adversarial review packet

Review target: working tree based on accepted Task 6 commit
`a1838742f1ed6e204278881efab3dcbd9f875acf`.

Initial Task 7 commit: `465e80d5f1cb67a5cd3aef2d932ea900b387d030`.
The reviewed snapshot also includes the current working-tree corrections to
this packet, `LOCAL_REPORT.md`, and
`tests/reference/test_numpy_reference_comparison.py`. Review the complete
change with `git diff a1838742f1ed6e204278881efab3dcbd9f875acf` plus
`git diff` before using the hashes below.

Please review read-only. Confirm that the NumPy reference is independent from
`src/aqt` at implementation level, faithfully models the accepted Task 6
semantics, uses only derived binary64 error bounds, and does not broaden scope
into production backtesting or Task 8. Check for look-ahead, incorrect
next-open timing, cost ordering, target/actual confusion, adverse-drift HOLD
violations, clipping errors, and untested boundary cases. Treat any numerical
or scientific-policy ambiguity as a blocking question rather than silently
choosing a convention.

Validation already run:

- focused reference tests: 37 passed
- full suite: 820 passed, 4 skipped
- Ruff reference checks: passed
- mypy src: passed (20 files)
- import contracts: 4 kept, 0 broken
- frozen audit: 28/28 trusted bytes, 14/14 sidecars, all bindings passed

Changed-file hashes:

```text
68a65e8f80eb34381cad798f69d970007a78db48d1fc4b5f9123d8a853fee3f1  tests/reference/__init__.py
ee578ccff74212c9707505a2d7fa8b9f56edafa1cbe08f71ea707df3aa49e873  tests/reference/_error_bounds.py
c9c47299739433178faef51a004e97d20ccd6e11fb404d1caa8607860346ec1d  tests/reference/_fixtures.py
0127a73db2bea2cfdefc38f0f91d42c598bfad5b3f2830110c63f02241672c42  tests/reference/_numpy_reference.py
14416d40f905eed12786ae9e01ce679de35f028d1b1a11898144a3f463faaf61  tests/reference/test_numpy_reference_comparison.py
14c307799c549635d09d54f234871fd101bc24c03c13f342fd81a40214495213  tests/reference/test_reference_band_tolerance.py
8263a407fdc5f0652c71bdc44319d1d62e856931df341d75c6d31e86c49fc59f  pyproject.toml
41b139b234571eeead61371fc23ab82eb16a694ca9cc251c0e1257e42dc4c018  review/task7/AUTHORIZED_SPEC.md
91d150538e336bde0e16221c418d24634d2384afdedf03da50833afe6fa8c7c9  review/task7/OPUS_PROMPT.md
```

`LOCAL_REPORT.md`, this packet, and `SOL_HIGH_REVIEW.md` are intentionally
excluded from the hash list because they describe the reviewed snapshot and
cannot contain stable self-hashes. Their complete contents are part of the
reviewed Git diff.

Return a severity-ranked finding list and a PASS/FAIL recommendation. Do not
edit, commit, or push.
