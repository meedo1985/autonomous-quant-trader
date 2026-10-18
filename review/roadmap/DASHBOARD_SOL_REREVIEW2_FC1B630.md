<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-18. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a14e59-9a0a-7121-80fe-4613b7cc3c90. Tokens used: 31,219. Packet built from dashboard-proposal fc1b630 (git show only): prompt DASHBOARD_REREVIEW2_PROMPT.md, DASHBOARD_SOL_REREVIEW_7753BA5.md, DASHBOARD_PROPOSAL.md. -->

# Sol re-review 2 of the dashboard proposal at fc1b630

## Review (final message, verbatim)

**Verdict: FIX.** DBR-1, DBR-2 and DBR-4 are resolved in the revised text. DBR-3 is only partly resolved: staging outside the served directory prevents a partial page from being served, but the proposal does not yet ensure that a directory listing is never served.

- **DBR2-1 — Medium — First startup can serve a directory listing.** If `aqt-web` starts before the first successful `index.html` publication, `http.server` lists the empty `www` directory. Require the first page to be published before the web unit starts, and test that startup order. Also narrow “any other path is refused” to “no other file is served”; the stated server maps URL paths to files rather than enforcing a URL allowlist. [Python `http.server` documentation](https://docs.python.org/3.11/library/http.server.html).

- **DBR2-2 — Low — The web account’s read restriction is overstated.** A separate account and `--directory` establish neither “it can read only that directory” nor the corresponding acceptance check. Specify the filesystem or systemd restrictions that make the intended boundary true, or say more narrowly that `aqt-web` cannot read the AQT data inputs. `SimpleHTTPRequestHandler` can also serve files outside its directory through a symbolic link placed inside it, so the served-directory check should exclude symlinks. [Python `http.server` security considerations](https://docs.python.org/3.11/library/http.server.html).

This is a review of the supplied proposal and adjudication, not verification of an installed server.

## Adjudication (Claude Opus 5.5, `claude-opus-5-5`, 2026-10-18)

| ID | Severity | Decision | Change to the proposal |
|---|---|---|---|
| DBR2-1 | Medium | Accept | `aqt-web` has `ConditionPathExists=.../www/index.html`; the install publishes a first page before enabling it; startup order tested. "Any other path is refused" narrowed to "no other file is served". |
| DBR2-2 | Low | Accept | Claim narrowed: `aqt-web` cannot read the AQT data, the deployment record or the code (`ProtectSystem=strict`, `ProtectHome=yes`, `InaccessiblePaths=/var/lib/aqt /etc/aqt /opt/aqt /opt/aqt-d19`). The served directory holds only the regular file `index.html`, never a symbolic link; the server check is `find ... -mindepth 1 ! -name index.html` printing nothing. |

No finding is left unrepaired.
