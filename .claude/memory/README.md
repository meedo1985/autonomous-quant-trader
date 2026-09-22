# Claude memory — repository copy

These files are a **copy for transport and backup**. Claude Code does not read
them from here.

The live location is outside the repository, per machine:

```
~/.claude/projects/D--PMP-programs-for-sharawi-autonomous-quant-trader/memory/
```

On Windows that is
`C:\Users\<you>\.claude\projects\D--PMP-programs-for-sharawi-autonomous-quant-trader\memory\`.

## Restoring on a new machine

Clone the repository, then copy the four memory files (not this README) into the
live location above, creating the directory if it does not exist:

```sh
# from the repository root, adjust the destination for your user
mkdir -p ~/.claude/projects/D--PMP-programs-for-sharawi-autonomous-quant-trader/memory
cp .claude/memory/MEMORY.md \
   .claude/memory/owner-constraints.md \
   .claude/memory/quant-trader-project-state.md \
   .claude/memory/ai-review-record-discipline.md \
   ~/.claude/projects/D--PMP-programs-for-sharawi-autonomous-quant-trader/memory/
```

The directory name is derived from the checkout path. If the repository sits at
a different path on the new machine, the derived name differs and the files must
go in the directory matching **that** path, not the one above.

`MEMORY.md` is the index loaded each session; the other three are the memories
it points at.

## Keeping the copy current

Nothing synchronizes these automatically. Claude updates the **live** files
during a session, which silently makes this copy stale. Refresh it by copying
back in the other direction before relying on it, and commit the result.

## What is here

| File | Type | Holds |
| --- | --- | --- |
| `MEMORY.md` | index | One line per memory |
| `owner-constraints.md` | user | The owner is not a statistician, cannot share the work externally, and will trade his own capital |
| `quant-trader-project-state.md` | project | Where the project stands, what is blocked, what to resume |
| `ai-review-record-discipline.md` | feedback | Commit a review record before citing it; never write the owner's review for him |

`owner-constraints.md` is personal context. It contains no credentials, no
account details and no figures, and this repository is **private**. Check that
visibility has not changed before adding anything more sensitive here.
