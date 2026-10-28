---
name: setup-sensemaking-skills
description: optionally configure a repository for sensemaking-skills by adding agent instructions, artifact contract references, workflow mode defaults, downstream skill mappings, and run-log conventions. use only when the owner explicitly wants this repository configuration; it is never a prerequisite for using-sensemaking, which works on an unconfigured repository.
---

# setup-sensemaking-skills

Optional legacy configuration Skill. It adds agent context and configuration artifacts for the older sensemaking-to-workflow pipeline. `using-sensemaking` needs none of them: it starts from the repository itself (ADR 0034), and this Skill's output is never a prerequisite for understanding, exploration or implementation.

## Workflow
1. **Explore**: Analyze the repository for existing agent instructions (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`) and documentation structures.
2. **Identify Context**: Locate the issue tracker, domain documentation, and existing skill ecosystems.
3. **Interactive Decisions**: Ask the user one decision at a time:
    - Target instruction file (e.g., `AGENTS.md`).
    - Default sensemaking path (`fast_path` vs `full_fog_path`).
    - Permitted execution modes (safety gates).
    - Downstream ecosystem mappings.
4. **Draft Changes**: Show the exact file modifications and new files to be created.
5. **Execute**: Write files only after explicit user approval.

## Artifacts Managed
- `AGENTS.md` / `CLAUDE.md` (Sensemaking Block)
- `docs/agents/sensemaking.md`
- `docs/agents/workflow-modes.md`
- `docs/agents/artifact-contracts.md`
- `docs/agents/downstream-skills.md`

## Boundary Rules
- **Non-Diagnostic**: This skill does not run the sensemaking pipeline or analyze project fog. It only handles configuration.
- **Approval Mandatory**: Never write or modify files without showing the diff and receiving approval.
- **One at a Time**: Ask interactive questions sequentially, not as a bulk list.

## References
- [Agent Block Template](references/agent-block-template.md)
- [Sensemaking Config Template](references/sensemaking-config-template.md)
- [Workflow Modes Template](references/workflow-modes-template.md)
