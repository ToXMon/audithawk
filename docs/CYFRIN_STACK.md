# The Cyfrin stack — how each repo integrates

All six repos verified live (git ls-remote, 2026-09-28). Pin commit hashes at
build time; re-verify before each phase. Licenses per-repo — check before any
commercial use.

| Repo | What it is | AuditHawk role |
|---|---|---|
| [`Cyfrin/cyfrin-audit-reports`](https://github.com/Cyfrin/cyfrin-audit-reports) | Public Cyfrin audit reports; **`reports_md/` is markdown** (no PDF extraction needed) | Corpus source #2 — index via `ml/ingest_reports.py` pointing at the markdown files |
| [`Cyfrin/security-and-auditing-full-course-s23`](https://github.com/Cyfrin/security-and-auditing-full-course-s23) | Patrick Collins' full security & auditing course | Curriculum for you; `finding_layout.md` is a ready-made report layout reference; select lessons become agent contextDocs |
| [`Cyfrin/web3-dev-containers`](https://github.com/Cyfrin/web3-dev-containers) | Maintained per-stack devcontainers (**foundry**, moccasin, lair, suimove, javascript, claude) | The sandbox base — replaces hand-rolled images in `infra/` (Phase 2). Foundry variants: `mounted` / `unmounted` |
| [`Cyfrin/audit-repo-cloner`](https://github.com/Cyfrin/audit-repo-cloner) | Python package that clones a repo and **prepares the report repo** (config examples for 1-repo / 2-repo / gitlab / mixed targets) | Contest intake: scaffolds a per-contest report workspace from the template |
| [`Cyfrin/report-generator-template`](https://github.com/Cyfrin/report-generator-template) | Spearbit-derived report generator (markdown findings → LaTeX → PDF: `main.tex`, `summary.tex`, `risk_classification.tex`) | The report-writer stage outputs this format; final PDF is the submission artifact |
| [`farrellh1/smart-contract-auditor-skill`](https://github.com/farrellh1/smart-contract-auditor-skill) | Claude Code skill: **370-item checklist, 13 categories**, sourced from `Cyfrin/audit-checklist` (Solodit-distilled) | The agent's review checklist (`references/*.md` loaded per-scope — matches our "load only what's relevant" context rule) and the eval rubric |

## Why this stack is the right one

- **The checklist solves coverage.** Ad-hoc LLM review misses bug classes
  outside its attention. 370 items across 13 categories, distilled from real
  Solodit findings, walked systematically per scope — that's how human audit
  firms work, and it converts directly into agent steps.
- **The report template solves output.** Contest judges and clients expect a
  specific report shape; generating into the Cyfrin/Spearbit format means the
  output is immediately credible and diffable.
- **The containers solve safety.** Isolation is Cyfrin's own "stay safe big
  dogs" answer — audited code runs in their maintained containers, not on the
  host. Aligns with the PCHS sandboxing ladder in `AGENT_DESIGN.md`.
- **The cloner solves intake.** Contest → workspace → report scaffold in one
  command, with configs for monorepo/multi-repo/gitlab targets.

## Wiring order

1. Phase 0/2: sandbox = `web3-dev-containers/foundry` (mounted variant for live
   edit-test cycles).
2. Phase 1: corpus = HF dataset + `cyfrin-audit-reports/reports_md/` + your
   reference PDFs. Same index, `source` tags distinguish them.
3. Phase 3: agent contextDocs += the skill's `references/INDEX.md` + the
   category files matching the audit scope; system prompt's review process
   becomes "walk checklist items for scope, cite item ids."
4. Phase 4: PoC loop unchanged (forge_test gate); per finding, the report
   draft uses `finding_layout.md` + the template's structure.
5. Phase 5: contest intake = `audit-repo-cloner` → report repo scaffold →
   agent fills it → human reviews → `generate_report.py` → PDF.
