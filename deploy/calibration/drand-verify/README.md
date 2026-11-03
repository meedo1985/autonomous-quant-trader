# drand round verifier (FP3, sheet step K)

Checks one round of the drand chain bound by FP3 (`review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE.md`, Rules 2 and 4).
Runs offline, on saved responses. It uses drand's own client, `drand-client` 1.4.2, with every dependency pinned in `package-lock.json`. Install scripts are not run.

```powershell
cd deploy\calibration\drand-verify
npm ci --ignore-scripts
node verify.mjs <chain-info.json> <round-response.json> <expected round>
```

It prints one JSON line. The exit code is 0 only when all of these hold:
- the chain info equals the bound hash, public key, scheme, period and genesis;
- the response's round is the expected round;
- the BLS signature verifies.

`randomness` is computed as the SHA-256 of the raw signature bytes, whatever the response says.

The test record, with real rounds and positive and negative cases, is `review/fp3/verifier-test-2026-10-25/RESULTS.txt`.
