# [VERIFY] result: CDX digest form for the capture record (DESIGN_SLICE6B rev 16 §2.1 item 3)

- Done by: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-15, while building slice 6b part 2 (B1).
- Status: **the design's item 3 fails on a real capture.** This is a finding against rev 16
  for the B1 review, not an approved change.

## What was checked

Public Internet Archive CDX row (fetched 2026-11-15):

```
info,blockstream)/api/block-height/0 20260905161311 https://blockstream.info/api/block-height/0 text/plain 200 NNVZIO5QLFHVIRULV75YOBX7EKNQDJMI 869
```

`id_` fetch `https://web.archive.org/web/20260905161311id_/https://blockstream.info/api/block-height/0`
without transfer decoding: 69 bytes, response header `content-encoding: gzip`,
`memento-datetime: Sat, 05 Sep 2026 16:13:11 GMT`.

| Bytes hashed | base32(SHA-1) | equals CDX digest |
|---|---|---|
| the 69 gzip bytes as served by `id_` | `NNVZIO5QLFHVIRULV75YOBX7EKNQDJMI` | **yes** |
| decoded body `000000000019d6...e26f` (64 ASCII chars, no newline) | `V5NX76AA23FZUGIDXPHNXUMNAO5JTO4N` | no |
| decoded body + `\n` | `OHSS7GJG2FCPUQWEPWIPDHCKMKPZQA7N` | no |

## Findings

1. The CDX digest is the SHA-1 of the payload **as stored**, here gzip-compressed by the
   origin server. It is not the SHA-1 of the decoded body. Rev 16 item 3 ("`body` hashes to
   `digest`") can never pass for a gzip-served capture, and gzip output is not reproducible
   from the body, so the module cannot recompute it.
2. The decoded body is exactly the 64-hex block hash with **no trailing newline** (rev 16
   item 2 is confirmed for blockstream.info; mempool.space was not checked: the archive's
   CDX search for it returned "Temporarily Offline" at the time).

## Proposed design change (for the B1 review; not applied to rev 16 text)

Schema `aqt.c2.capture_record.v2` (v1 was never used), field set
`{schema, url, timestamp, status, digest, payload, content_encoding, body, acceptance_record_sha256}`:
- `payload`: base64 of the exact `id_` response bytes (no transfer decoding);
- `content_encoding`: `"identity"` or `"gzip"` (anything else refused);
- item 3 becomes: base32(SHA-1(payload)) == `digest`, and `body` == payload decoded by
  `content_encoding` (ASCII);
- items 1, 2 and 4 unchanged. The SPEC §5 binding of the `id_` fetch to the CDX row
  (same URL, timestamp and digest) is what this checks offline.

The known capture above is to be used as the known-answer test.
