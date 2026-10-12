# Fable focused check of the REG-1/REG-2/O-8 proposal rev 2 at `cc8c89c`: NOT READY

Date: 2026-10-04.
Anthropic-family focused check for R19-2, run from prompt `REVIEW_PROMPT_R2.md`
with prefix FR2, in parallel with Sol SR2 and without sight of it.

The model ID is self-reported, because Fable subagent transcripts come back
empty. The hand-back is recorded below verbatim by Claude Opus 5.5
(`claude-opus-5-5`). No finding is omitted.

---

**Model:** Claude Fable 5.1 (`claude-fable-5-1`), Anthropic Claude family (self-reported)
**Commit checked:** `cc8c89c` (`review/governance-statistics-amendment/reg-o8-proposal/PROPOSAL.md`, revision 2)
**Prompt:** `REVIEW_PROMPT_R2.md`, PREFIX = FR2
**Verdict: NOT READY** (two blockers, FR2-1 and FR2-2; both can be fixed by editing text, with no new analysis)

**Read:**
- PROPOSAL rev 2;
- `ADJUDICATION_370C50C.md`;
- `FABLE_REVIEW_370C50C.md`;
- DRAFT_WORDING §2.0, §2.4 and §7;
- the D-14/D-15 addendum Q5;
- protocol l.110–130;
- `factory.py` FEATURE_NAMES;
- `canonical.py` l.25–55 and l.450–453.

**Not done:** no network, no confirmation or lockbox data, no reading of
SOL_REVIEW_370C50C.md or of any other-family review of rev 2, no edits.

**Resolution of FR1:**
- Resolved: FR1-1, FR1-3, FR1-4, FR1-5, FR1-6, FR1-7, FR1-8, FR1-9.
- FR1-2 and FR1-10 are resolved in §1 and §2 but not carried into the owner
  questions (FR2-2).
- FR1-2's `ewma_vol_168h` mention was repaired incorrectly (FR2-3).

**Checked and confirmed (no finding):**
- the §2 E-DIFF and E-IMPROV statements;
- the withdrawal of "carries over";
- the REG-1 (a) consequence that the 10% rule is not tested;
- the O-8 section;
- the O-9 invalidation examples, which match DRAFT §2.0 `first_post_rule` and
  `failure`;
- "each invalidation costs one halving", which matches
  `invalidation_after_post` (m increments);
- the risk-per-stop figures of 0.05% and 0.5%.

**"Very unlikely to pass" (Q2a)** is defensible as worded. At small `c`,
C − B ≈ −B, so E-DIFF ≈ −Sharpe(B). A pass needs the benchmark's realized
Sharpe over the window to be below about −z_crit·SE. That is rare when BTC
drift is at least 0, and it happens at roughly the α level when drift is 0.
The proposal says "unless the benchmark did poorly" and labels the claim
qualitative. Its inference is the problem, not its probability: see FR2-4.

| ID | Severity | Location | Evidence | Proposed disposition |
|---|---|---|---|---|
| FR2-1 | BLOCKER | §4 Sigstore Rekor candidate; §6 Q4 | (1) §4 says Rekor must be "checked against official Sigstore documentation before the question is asked", yet Q4 names it to the owner as "to be verified". The question cannot go out in that state. (2) DRAFT §2.0 `first_post_rule` makes every message at the identity count, and a second post invalidates. That requires enumerating *all* entries for the identity. §4 asserts "entries are searchable by identity". From memory, unverified: the newer tile-based Rekor (v2) dropped v1's online search/index API, and the v1 public instance is being frozen or sharded. If so, requirement (1) plus the first-post rule cannot be checked from the log alone. (3) §4 does not show how requirement (4), "captured by an independent archive at posting time", is met. Rekor is the log itself; whether witnesses or monitors count as an independent archive is not argued. (4) Sigstore keyless signing puts the OIDC identity (an email or GitHub account) in a public certificate in the log. Q4 says the post "reveals nothing about your strategies" but omits that it publicly reveals the signing identity. That matters to an owner who cannot share the work. A self-managed key avoids this but changes how authentication works. | Verify Rekor against official documentation before asking: v1/v2 status, search by identity or key, retention, and how requirement (4) is met. Then rewrite §4 and Q4, stating what the post reveals about the poster (identity or key) and which signing mode is meant. If Rekor fails, give no candidate and ask only the third-party alternative. (These are reviewer recollections and are also unverified.) |
| FR2-2 | BLOCKER | §6 Q1 and Q2 as a pair; §2 "Under REG-2 (b), or through a proxy under (a), an approximately fixed size can still be written" | The two answers interact, but the questions are presented as independent. (i) REG-1 (a) "Not in C2" with REG-2 (b) "Allow" makes `s = 0.10·σ̂/τ` a legal registration, so the 10% rule *can* be registered in exact form, contradicting Q2 (a) "not in C2". (ii) Under REG-2 (a), §2 says an approximately fixed 10% stays writable through `rv_720` and similar features. Q2 (a) tells the owner only "Your 10% rule itself is not tested". It does not say that a near-10% registration stays possible, and that it would face the §1 misalignment (a plain fixed size tends to fail G-11) as well as the small-`c` DSR problem. This is the residue of FR1-2 and FR1-10 that never reached the questions. | Ask Q1 and Q2 as one combined question, or add to each: "If you answer (b) to Q1, 'not in C2' cannot hold exactly; under either answer an approximately fixed size can be written through other volatility features, and such a registration is judged unreliably by the random-timing check." |
| FR2-3 | MAJOR | §1 "frozen features include … `ewma_vol_168h`" listed as a proxy; option (a) | `canonical.py` l.54–55 and l.450–453, with `factory.py` l.63 and l.355: the `ewma_vol_168h` feature is *identical by construction* to the default sizing estimator `EWMA_168h` (protocol l.114). For a default-sizing trial it is σ̂ itself, not a proxy. Option (a)'s "the sizing estimator's output" does not say it excludes a named feature. Read literally, a declaration listing `ewma_vol_168h` gets exact cancellation, which is the one route (a) claims to stop. For non-default-sizing trials it is a legal close proxy. Banning it also takes away the most natural input for honest variance-timing signals, which D-14 Q3 (a) credits; this is not disclosed. | State that under (a) the banned set is the sizing estimator's output *and any frozen feature identical to it* (currently `ewma_vol_168h` when sizing is `EWMA_168h`), with the mapping bound under `<<OPEN D-20>>`. List `ewma_vol_168h` as a proxy only for non-default-sizing trials. Disclose the small loss for honest variance-timing signals. |
| FR2-4 | MAJOR | §2 option (b) "This is the only route that tests the 10% rule as such"; §6 Q2 (b) "This is the only way to test 10% itself … very unlikely to pass" | §2's own analysis shows that at small `c` the DSR verdict on E-DIFF ≈ −Sharpe(B) is decided mostly by the benchmark's window, not by the owner's idea. A fail is uninformative about the rule. A pass, which needs a poor benchmark window, is also mostly uninformative, and a near-flat candidate with no skill could pass in such a window. Only the E-IMPROV gates (G-1, G-4, G-8, G-11) actually test the idea at 10%. "Very unlikely to pass" tells the owner his 10% probably *fails*; the accurate message is that the main test would *barely look at* the 10% rule. Q2 (b) also invites reading a fail as evidence against the idea, which the body text ("a property of the decided selection rule, not of the owner's idea") explicitly rejects. | Reword (b) and Q2 (b): "It tests your 10% rule on the improvement checks, but at 10% the main promotion test mostly measures how the benchmark did over the window, not your rule: a fail says little about your idea, and so would a pass. Promotion is very unlikely unless the benchmark had a poor window." |
| FR2-5 | MINOR | §1 "This is the residual the owner already accepted under D-14 Q3 (a), consequence (2)"; Q1 (a) "That residual is the one you already accepted in D-14" | Addendum Q5 (2) accepted only that "a signal that only reacts to volatility can pass the random-timing check with no price-direction skill". The REG-2 residual is wider. G-11 measures sizing misalignment, which can also *fail* a candidate unrelated to its timing (a plain proxied fixed size tends to fail; FR1-3, restated in rev 2 §1). It can also pass a deliberately built one through misalignment rather than variance timing. The owner accepted the pass direction for a different mechanism, not this one. | Say "closely related to" rather than "the one you already accepted", and add the fail direction to Q1. |
| FR2-6 | MINOR | §1 "A signal can also recompute `σ̂` from raw returns" | Under (a)'s run-time restriction, `s` receives only declared feature values, and the frozen features have no hourly return history of the kind needed to rebuild a 168 h EWMA. Recomputation needs a model with its own history access, which `s_inputs` (model ids) would have to permit. The proxy route alone supports the conclusion. | Qualify as "or recompute it, if a declared model has access to return history", or drop the sentence. |
| FR2-7 | MINOR | §6 Q5 (b) "ends promotion for **both** families" | DRAFT R-4: no post-v1 window is eligible *until a later amendment*. So promotion ends until a further amendment creates a new window, not permanently. As worded, (b) sounds more final than it is, which tilts the question toward (a). | Add "until a later amendment creates a new eligible window". |
| FR2-8 | MINOR | §6 Q3 (O-8) | The question says the change is limited to exits-to-zero but omits that every benchmark's specification text, and so its hash, changes (§3 states this). The values are expected unchanged, and Q3 already says this is unverified. Harmless but incomplete. | Add "the benchmark definitions get new hashes; their values are expected not to change". |
| FR2-9 | MINOR | ADJUDICATION "Follow-up for Annex C" | The `ewma_vol_168h` identity (FR2-3) and the joint Q1/Q2 consequence (FR2-2) are missing from the C-10 (1) follow-up. | Add both to the C-10 (1) follow-up for the next Annex C revision. |

**Summary for the owner (three lines):**
1. The sizing and fill-rule analysis is now correct; in particular it no longer claims a vol-target test tells you how 10% would do.
2. Two questions are not ready yet. The public-post channel (Sigstore) must be checked before you are asked, and it may publicly show who signed. The "ban" and "fixed 10%" questions affect each other and must be shown together.
3. If a fixed 10% were tested, the main promotion test would mostly measure how the benchmark did, not your rule, so neither a pass nor a fail there would tell you much about your idea.
