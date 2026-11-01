# Sol review of 3ba1bef (freeze runs T1b)

- Reviewer: Codex `gpt-6-sol`, reasoning effort high, `codex exec -s read-only` (model line from the run log: `model: gpt-6-sol`), 2026-11-01.
- Prompt: diff f715dfe..3ba1bef plus context and validation evidence (IDs T1BF-S-n).
- Verdict: **FIX** (one finding, T1BF-S-1).

## Report (verbatim)

What this change does: `freeze` now checks the build commit’s screen vectors in the pinned image before building the qualification object. The build commit is the right source: `qobj.build` copies its `screen.py` into the object, and `declare()` checks the loaded screen against that copy.

**Must fix**

1. **T1BF-S-1 — Other engine commands can mount the wrong checkout.** [d19.sh](D:/PMP-programs-for-sharawi/autonomous-quant-trader/deploy/calibration/d19.sh:127) uses `${CODE:-$APP}`, but `CODE` is initialized only inside `freeze`. If root invokes `screen-pilot` with an inherited nonempty `CODE`, it runs the alternate checkout at `/app` while the image tag still comes from `$APP`. Initialize `CODE=""` beside `NET=none`, and test the inherited-variable case. The current launcher test checks the assignments’ text but misses this behavior.

The vector call itself is ordered correctly: `CODE` is set and cleared on separate lines, the call has no network, and a mismatch exits before object creation. The clone is owned by uid 990 and is readable through the read-only mount; bytecode writes are disabled. I found no further path in this change that lets a vector mismatch proceed.

**Verdict: FIX.** I independently checked `sh -n`, `git diff --check`, and the clean working tree. The reported Windows suite passes are off-image; the pinned-image CI result and main-suite result remain outstanding. This read-only review has not been committed as the repository requires for a completed review record.

## Adjudication

- T1BF-S-1: accepted and repaired in the next commit: `CODE=""` initialised beside `NET=none`, so an inherited `CODE` never reaches `engine()`; test added. (Under the documented `sudo sh d19.sh`, sudo's default env_reset would already drop it; the repair does not rely on that.)
- The reviewer's note that the pinned-image result is outstanding stands: CI's launcher job is the first in-image run of T1b, and the main suite result (1856 passed, 9 skipped) arrived after the prompt was sent.
- No finding left unrepaired.
