# Independent adversarial review: the freeze sheet's FP2 update at 99ef780

You are an independent adversarial reviewer (read-only), not an authority;
the owner's §16 PR review is separate. Review `git diff a6ce8fd 99ef780` on
branch `freeze-sheet` (PR #76; included below): the DRAFT sheet
`deploy/calibration/FREEZE_HELDOUT.md` updated to the FP2 build of branch
`fp2-freeze-launcher` (PR #77, head `500f1ff`; read its `deploy/calibration/d19.sh`
with `git show fp2-freeze-launcher:deploy/calibration/d19.sh`, and the review
records `review/d19-engine/ASTRA_FP2_BUILD_*.md` and `ADJUDICATION_FP2_BUILD_*.md`
there). This closes finding FP2-R2 (b): the owner-run procedure that installs
and verifies `/opt/aqt-d19/build`, with both full commit ids, origin and
ownership checked and the evidence recorded before step G.

Check: (1) does the sheet now match the launcher exactly (command names,
argument order, what each prints and refuses, where files go); (2) does G0
close FP2-R2 (b), and can the owner follow it line by line on Ubuntu as root
via sudo (quoting of the `find` line, what each line prints); (3) any
procedural gap or ordering problem (G0 before FP1-FP4, the network need of
step G). The owner runs each line alone and sends output; the AI never logs
in. Findings get IDs `FS2-R1`, ... with severity, place, failure scenario and
repair. Then a verdict: ACCEPT or FIX.

## The diff

```diff
diff --git a/deploy/calibration/FREEZE_HELDOUT.md b/deploy/calibration/FREEZE_HELDOUT.md
index b2888d0..7ae9f9e 100644
--- a/deploy/calibration/FREEZE_HELDOUT.md
+++ b/deploy/calibration/FREEZE_HELDOUT.md
@@ -14,24 +14,41 @@
 | # | Precondition | Source | State |
 |---|---|---|---|
 | FP1 | FULL_RUN.md steps E and F done: `Exited (0)`, all 104 ids at `24 dev/`, and `choices.json` received with `qualifies` true and `margin_ok` true (`d19.sh choose` exit 0). Exit 3 (`margin_failed`) goes to you to decide (I1-6) | FULL_RUN.md E, F; `calibration/qobj.py` `build` | open (run going) |
-| FP2 | A merged build change, with Sol's review and **your §16 PR review**: (a) `d19.sh freeze`, which runs `qobj.build` inside the pinned image with the run's checkout `/opt/aqt-d19/app` (`eeaa728`) as `run_root` and a second, read-only checkout of the merged build commit as `root`; (b) `d19.sh heldout <n> <round> <randomness>` and `d19.sh certify <n>`, which run `scripts/d19_heldout.py run` and `certify` the same way, plus a `heldout-status` that shows chunk counts only (P18-6); (c) `review/d19-engine/FREEZE_REVIEWS.json`, listing `mapping.py`, `screen.py` and `heldout.py` with their SHA-256 and a committed review record each. Without (c), `build` refuses (BO-4, QO-5). (d) **Installed**: the new launcher lives in that second checkout, `/opt/aqt-d19/build` at `<<BUILD_COMMIT>>`, verified as the full commit there, while `/opt/aqt-d19/app` stays at `eeaa728`; the build change says how, and FP2 holds only once that check passes on the server (FH-5) | `calibration/qobj.py` (`LATER`, `REVIEWED`, `FREEZE_REVIEWS`); `d19.sh` has none of these commands at `eeaa728` | **open** |
+| FP2 | A merged build change, with its independent review and **your §16 PR review** (PR #77; Astra reviews `ASTRA_FP2_BUILD_*.md`, last ACCEPT at `05321c5`): (a) `d19.sh freeze <build commit>`, which runs `qobj.build` inside the pinned image with the run's checkout `/opt/aqt-d19/app` (`eeaa728`) as `run_root`, and as `root` a disposable clone, owned by uid 990, of a second, root-owned checkout of the merged build commit (`build` fetches the live remote into the clone, QO-2, so `freeze` is the one engine command with network, BUILD-1). It refuses unless that checkout is at exactly the commit you name, unmodified, and writable by root only; (b) `d19.sh heldout <attempt> <posted hash> <round> <randomness>` and `d19.sh certify <attempt> <posted hash>`, which run `scripts/d19_heldout.py run` and `certify` from `/app`, plus a `heldout-status` that shows state, times and chunk counts only (P18-6); `certify` runs once per attempt and prints its report; (c) `review/d19-engine/FREEZE_REVIEWS.json`, listing `mapping.py`, `screen.py` and `heldout.py` with their SHA-256 and a committed review record each. Without (c), `build` refuses (BO-4, QO-5). (d) **Installed** by step G0: `/opt/aqt-d19/build` at `<<BUILD_COMMIT>>`, verified as the full commit there, root-owned, with the repository's GitHub origin, while `/opt/aqt-d19/app` stays at `eeaa728`; FP2 holds only once G0's checks pass and their output is recorded (FH-5, FP2-R2) | `calibration/qobj.py` (`LATER`, `REVIEWED`, `FREEZE_REVIEWS`); `d19.sh` has none of these commands at `eeaa728`; PR #77 | **open** (PR #77 awaits your review) |
 | FP3 | **The drand chain is fixed, by chain hash and public key, before step G.** Prereg §8 takes the round from "the C2 drand chain (DRAFT §2.0)", and DRAFT §2.0 leaves that chain as `<<SIGNING: chain hash, public key>>` in the unsigned C2 draft; a draft placeholder binds nothing. Until a formal step binds it, the held-out anchor has no defined input. It must be bound before the post at the latest: a chain chosen once beacon outputs are known would let its choice pick the outcome. The same step settles whether DRAFT §2.0's failure rule (no verifying output within 7 days of the round's scheduled time) applies to D-19 (step K) | prereg §8; `review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md` lines 161, 165, 340 | **open, governance** (Constitution amendment process or C2 signing; AI cannot author, merge or activate it) |
 | FP4 | A verifier Bitcoin Core node, version 30.0 or later, `-blockfilterindex=1`, keeping every block from height 972,269 (`F_Q1`) to the freeze read. A pruned node is enough if its prune target keeps that range (block filters with pruning: upstream PR #15946; confirm in the 30.x docs before use). It needs an initial sync of the whole chain, about 1-3 days of download. It also gives the fee estimate for the post (step H). Where it runs is your decision (Q-F1) | O-6a SPEC §4, §7 | **open, your decision** |
 | FP5 | The Electrum 4.8.2 wallet holding `A_Q1`'s key is on your laptop, and both explorers show `A_Q1` never spent from and holding only `F_Q1` (OF1-3), checked on the day of the post | KEY_RECORD_DRAFT.md; ACCEPTANCE_RECORD.md §2 | checked on the day |
 | FP6 | The post can be included by `D_Q1` = 1,000,000. `F_Q1` (5,500 sat) covers a fee rate up to about 30 sat/vB with change above dust, so the post waits for fees below that | ACCEPTANCE_RECORD.md | checked on the day |
 
-Until FP1-FP4 hold, nothing below runs. That is the intended guard.
+Until FP1-FP4 hold, nothing below runs, except step G0, which is how FP2 (d) comes to hold; it runs only after PR #77 is merged. That is the intended guard.
 
 **Run every line on its own, one at a time; never paste a block. If any line fails, or prints an error, `refused`, `STOP` or `FAIL`, stop there and send me the output.**
 
+## G0. Install the build checkout (minutes; FP2 (d))
+
+After PR #77 is merged, I fill `<<BUILD_COMMIT>>` with its full merge commit. One line at a time:
+
+```sh
+sudo git clone --quiet https://github.com/meedo1985/autonomous-quant-trader.git /opt/aqt-d19/build
+sudo git -C /opt/aqt-d19/build checkout --quiet <<BUILD_COMMIT>>
+sudo chmod -R go-w /opt/aqt-d19/build
+sudo git -C /opt/aqt-d19/build rev-parse HEAD
+sudo git -C /opt/aqt-d19/app rev-parse HEAD
+sudo git -C /opt/aqt-d19/build remote get-url origin
+sudo git -C /opt/aqt-d19/build status --porcelain --untracked-files=all
+sudo find /opt/aqt-d19/build \( ! -user 0 -o -perm /022 \) -print -quit
+```
+
+Check: the first `rev-parse` prints `<<BUILD_COMMIT>>`; the second prints `eeaa7282e3b7c87790c162d679016c290d5f4ea5`; the origin is the GitHub address above; the last two lines print nothing. **Send me** the output. I record it, and FP2 holds from then. `/opt/aqt-d19/app` is not touched.
+
 ## G. Build and commit the qualification object (hours)
 
 ```sh
 cd /opt/aqt-d19/build/deploy/calibration
-sudo sh d19.sh freeze
+sudo sh d19.sh freeze <<BUILD_COMMIT>>
 ```
 
-It prints `qualification_object_sha256` and writes the object directory `/var/lib/aqt-d19/qobj-1`, or refuses with nothing written. **Send me** the hash. Then copy the directory to your laptop, in a Windows terminal (FH-7; the same `scp` as the dashboard's copy, with your server's address):
+It checks the build checkout again (the same commit, unmodified, root-only), prints `build checkout ..., unmodified`, then `qualification_object_sha256` and writes the object directory `/var/lib/aqt-d19/qobj-1`, or refuses with no object published (only its own scratch clone `/var/lib/aqt-d19/freeze-root` may change). It needs the server's Internet connection: it reads the repository's branches from GitHub. **Send me** the hash. Then copy the directory to your laptop, in a Windows terminal (FH-7; the same `scp` as the dashboard's copy, with your server's address):
 
 ```bat
 scp -r root@<<SERVER>>:/var/lib/aqt-d19/qobj-1 "%USERPROFILE%\Desktop\qobj-1"
@@ -96,7 +113,7 @@ An invalidation not listed in this record counts as found at or after the start
 
 ```sh
 cd /opt/aqt-d19/build/deploy/calibration
-until [ "$(date -u +%s)" -ge <<START_EPOCH>> ]; do sleep 5; done; sudo sh d19.sh heldout 1 <<ROUND>> <<RANDOMNESS>>
+until [ "$(date -u +%s)" -ge <<START_EPOCH>> ]; do sleep 5; done; sudo sh d19.sh heldout 1 <<QUALIFICATION_OBJECT_SHA256>> <<ROUND>> <<RANDOMNESS>>
 ```
 
 The first part waits until record 2's time `S` (`<<START_EPOCH>>` is `S` in seconds; I fill both). Run it in good time before `S` and leave the window open until it prints that the run started.
@@ -109,7 +126,7 @@ The first part waits until record 2's time `S` (`<<START_EPOCH>>` is `S` in seco
 
 ```sh
 cd /opt/aqt-d19/build/deploy/calibration
-sudo sh d19.sh certify 1
+sudo sh d19.sh certify 1 <<QUALIFICATION_OBJECT_SHA256>>
 ```
 
 Exit 0: every test is within its target (§6). Exit 2: not. Either way, **send me** the report; I commit it.
```
