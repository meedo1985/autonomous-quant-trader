<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-18. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a14e5e-5290-7d83-8c69-1bd312ef8d31. Tokens used: 59,007. Packet built from dashboard-proposal 91150a5 (git show only): prompt DASHBOARD_REREVIEW4_PROMPT.md, DASHBOARD_SOL_REREVIEW3_AFE4B2B.md, DASHBOARD_PROPOSAL.md. -->

# Sol re-review 4 of the dashboard proposal at 91150a5

## Review (final message, verbatim)

**Verdict: FIX.** Removing the web server resolves DBR3-1, and removing ACLs resolves DBR3-2. The replacement design still makes claims its settings do not establish.

- **DBR4-1 — Medium — `PrivateNetwork=yes` does not prevent all communication.** Filesystem `AF_UNIX` sockets remain reachable, and read-only mounts do not block communication with them. Thus “cannot send anything anywhere” is unsupported. Constrain the IPC paths that matter to the trading app, test them, and narrow the claim to the isolation actually established. [systemd.exec](https://www.freedesktop.org/software/systemd/man/257/systemd.exec.html)

- **DBR4-2 — Medium — The filesystem and capability claims are too absolute.** `ProtectSystem=strict` excludes `/dev`, `/proc` and `/sys` from its read-only mount, so “writes only its own directory” does not follow. `CAP_DAC_READ_SEARCH` bypasses file read and directory search permissions for reachable paths; it does not make every server file readable, since `ProtectHome=yes` and `InaccessiblePaths=` hide paths. State those limits accurately and test any write or read boundary on which the design relies. [systemd.exec](https://www.freedesktop.org/software/systemd/man/257/systemd.exec.html), [capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html)

- **DBR4-3 — Low — The copy step is not yet assured.** Mode `755` on `page/` and `644` on `index.html` do not establish that the owner’s SSH account can traverse `/var/lib/aqt-dashboard`; its mode is unspecified. `Desktop/aqt-dashboard.html` is also relative to the launcher’s working directory. Specify the parent’s access, use a definite local destination, and add an end-to-end `scp` check using the owner’s account after the first successful generation. [path_resolution(7)](https://man7.org/linux/man-pages/man7/path_resolution.7.html), [scp(1)](https://man.openbsd.org/scp)

This reviews the supplied proposal; I could not verify an installed unit or perform the proposed copy.

## Adjudication (Claude Opus 5.5, `claude-opus-5-5`, 2026-10-18)

| ID | Severity | Decision | Change to the proposal |
|---|---|---|---|
| DBR4-1 | Medium | Accept | `RestrictAddressFamilies=none` added: no socket of any family, Unix included. Claim narrowed to that; tested on the server (inet and Unix socket). |
| DBR4-2 | Medium | Accept | `PrivateDevices=yes`, `ProtectKernelTunables=yes`, `ProtectControlGroups=yes`, `ProtectProc=invisible` for `/dev`, `/proc`, `/sys`. Capability claim narrowed to "paths visible to it". Only tested boundaries are claimed, each listed. |
| DBR4-3 | Low | Accept | `/var/lib/aqt-dashboard` mode `755`; absolute local destination; end-to-end copy with the owner's Desktop file is an acceptance item. |

No finding is left unrepaired.
