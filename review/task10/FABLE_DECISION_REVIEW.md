# Claude Fable 5.1 Task 10 decision review

Date: 2026-09-14

Observed model metadata: `claude-fable-5-1`.

## Verdict

`PASS` for a deterministic preregistration registry as Task 10.

Fable found that this task can remain outside Constitution section 16's
protected protocol-enforcement scope only while it provides identity, immutable
storage, deterministic enumeration/seed derivation, verification, and pure
read-side counts. Any budget stop, permission to begin, protected hash
acceptance, cycle binding, confirmation/lockbox access, result evaluation, or
promotion decision remains excluded.

Fable selected this task ahead of data ingestion, metrics, promotion, and cycle
binding because no approved real dataset exists, the frozen metrics schema is
skeletal, and promotion/cycle enforcement is protected. It required explicit
choices for self-hash removal, seed encoding, and trial-index scope; those
choices are recorded in `AUTHORIZED_SPEC.md`.

## Required adversarial cases

- canonical key ordering and CRLF normalization inside string values;
- content sensitivity and frozen-schema validation;
- a fixed seed byte/vector and single-input perturbations;
- deterministic parameter/horizon enumeration;
- concurrent Windows writers;
- torn trailing line and altered history detection without repair;
- append refusal on any invalid existing chain;
- read-side accounting without policy decisions.

The initial Fable invocation used tools to inspect the repository and exhausted
its response stream. The same exact session was resumed with tools disabled;
the verdict above was recovered from Claude Code's local session transcript.
