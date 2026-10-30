# Applicable policy provenance

Phase 2 read the global Codex AGENTS.md and the full 936-line instruction sheet (Library `REQ-001`). The local NPU workspace has no additional AGENTS.md found at its applicable ancestor paths. Project-KISS instructions do not extend into this repository.

The canonical policy was successfully read through the GitHub connector in this phase, resolving the phase-1 lookup gap:

| File | Retrieved source | Git blob identity |
|---|---|---|
| Operating principles | [i-pp/ai-orchestration, docs/ai/orchestration.md](https://github.com/i-pp/ai-orchestration/blob/main/docs/ai/orchestration.md) | fc46d44e2d68fdcbadca143c91dec2097a7a732a |
| Permission boundaries | [docs/ai/policies.md](https://github.com/i-pp/ai-orchestration/blob/main/docs/ai/policies.md) | bdb98dba067f4a867b928e26da55720bb73fea42 |
| Agent responsibilities | [agents/README.md](https://github.com/i-pp/ai-orchestration/blob/main/agents/README.md) | da452dcda9246a711d7f6263575162516038eaf8 |

These are retrieved blob identities, not a fabricated local policy or a claim that a mutable `main` link never changes. The applicable task authorizes bounded work only in this new repo, preserving the original environments. Routine read-only inspection and reversible local edits proceed; generated work is validated before handoff; hardware execution/install/publication remain outside this phase. No lower-level policy expands user authorization.
