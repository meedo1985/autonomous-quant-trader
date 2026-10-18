<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-18. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a14e5b-abed-7b42-b791-61571248d49b. Tokens used: 38,030. Packet built from dashboard-proposal afe4b2b (git show only): prompt DASHBOARD_REREVIEW3_PROMPT.md, DASHBOARD_SOL_REREVIEW2_FC1B630.md, DASHBOARD_PROPOSAL.md. -->

# Sol re-review 3 of the dashboard proposal at afe4b2b

## Review (final message, verbatim)

**Verdict: FIX.** DBR2-2 is resolved: the proposal now names systemd restrictions for the web account and requires an installed-server check. DBR2-1’s *first-startup* case is resolved, but the broader promise that no directory listing can be served remains unsupported.

- **DBR3-1 — Medium — A running server can still list `www` if `index.html` disappears.** `ConditionPathExists=` is checked when the unit starts, not on each request. With no index file, `http.server` generates a directory listing. Make listing impossible at request time—for example, deny `aqt-web` directory read permission while retaining traversal and file read permission—and test a request after removing the page. [systemd unit conditions](https://www.freedesktop.org/software/systemd/man/257/systemd.unit.html), [Python `http.server`](https://docs.python.org/3.11/library/http.server.html).

- **DBR3-2 — Low — The generator ACL claims exceed what default ACLs establish.** “New files stay readable” is not guaranteed: creation mode can mask inherited read access, and a file renamed into a directory does not acquire that directory’s default ACL. Granting default read access within an input directory also does not establish “read access only to the input files above.” Specify access against the app’s actual file creation and replacement behavior, test it, and narrow the read-access claim. [Linux ACL rules](https://man7.org/linux/man-pages/man5/acl.5.html).

This is a review of the supplied proposal, not verification of an installed server.

## Adjudication (Claude Opus 5.5, `claude-opus-5-5`, 2026-10-18)

Both findings are accepted. Rather than add a further guard for each serving edge case, the revision removes the web server and the ACL scheme.

| ID | Severity | Decision | Change to the proposal |
|---|---|---|---|
| DBR3-1 | Medium | Accept | No web server at all. The owner copies the finished page over SSH (`scp`) and opens it locally. Directory listing, bind address, symbolic links and the tunnel no longer exist. Acceptance: no listening port is added. |
| DBR3-2 | Low | Accept | No ACLs. The generator unit reads through `CAP_DAC_READ_SEARCH` (its only capability), inside `ProtectSystem=strict` with `ReadWritePaths=/var/lib/aqt-dashboard`, `InaccessiblePaths=/etc/aqt/telegram`, `PrivateNetwork=yes`, `NoNewPrivileges=yes`, `ProtectProc=invisible`. The read claim is narrowed to "can read the server's files except the credential, writes only its own directory, cannot send anything". Checked on the server inside the same sandbox. |

No finding is left unrepaired.
