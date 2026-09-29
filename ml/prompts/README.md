# Prompt registry

Every LLM node in `machine/audit-graph.yaml` owns a versioned prompt here —
never inline in code.

| prompt_id | file | node |
|---|---|---|
| `scope-parse` | `scope-parse.prompt.md` | scope — parse scope.json, select checklist categories |
| `hypothesis` | `hypothesis.prompt.md` | hypothesize — grounded vulnerability hypotheses |
| `poc-engineer` | `poc-engineer.prompt.md` | write_poc — Foundry PoC authoring |
| `report-writer` | `report-writer.prompt.md` | draft_report — platform-format findings |

## Format

Each file: frontmatter (`prompt_id`, `version`, `node`, `changelog`) then the
prompt body. Forge loads by id at session start.

## Rules

1. Changes go through `ml/optimize_prompts.py` (AdalFlow) once an eval baseline
   exists — no hand-edits without a before/after eval run.
2. Promotion requires beating the current version on the full held-out suite.
3. Every version + scores is archived under `<id>/versions/` — revertible.
4. The agent's overall system prompt (`agent/audithawk.ts`) holds the
   *operating contract* (rules 1–7); node prompts hold the *task craft*.
