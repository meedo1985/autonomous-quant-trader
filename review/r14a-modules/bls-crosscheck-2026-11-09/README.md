# Cross-check of the module's BLS verifier against drand's own client (2026-11-09)

- What: `calibration.c2_confirmation.bls_verify` (route M, standard library only) versus
  the FP3 verifier `deploy/calibration/drand-verify/verify.mjs` (`drand-client` 1.4.2,
  `npm ci --ignore-scripts` from its `package-lock.json`, from `origin/freeze-sheet`), with
  the FP3 chain-info file `review/fp3/drand-info-2026-10-25/52db9ba7….info.json`.
- Rounds: 1, 2, 3 and 800000k + 12345 for k = 1..37 (to round 29,612,345), fetched from
  `https://api.drand.sh/v2/chains/52db9ba7…/rounds/<r>` (public, no credentials) and saved
  in `crosscheck_rounds.json` (SHA-256 of their sorted canonical JSON
  `21d32ea7b7d523433724d2a1ba63156bc975d7b38e041dc81b00d8474cceee6f`).
- Cases: each real round, and each round with the next listed round's signature.
- Result (`crosscheck_rows.json`): **80 checks, 80 agree**; every real round verifies and
  every swapped one does not, in both. Python time 0.71 s per check (Windows 11, Python 3.14).
- Command: `python -I crosscheck.py <repo> <drand-verify dir>` (the script is here).
