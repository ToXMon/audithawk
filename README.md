# 🦅 AuditHawk

An AI agent for smart-contract security work: point it at an audit opportunity
(Code4rena / Sherlock / Cantina contest, Immunefi bounty) and it ingests scope,
runs static analysis, does LLM deep review grounded in a knowledge base of real
audit findings, writes and **executes Foundry PoCs**, and drafts the submission
package — with a human making every final call.

Built on the [Forge](https://github.com/ToXMon/forge) agent harness. Personal
use first; product later.

> **Status:** scaffold. See [`docs/BUILD_GUIDE.md`](docs/BUILD_GUIDE.md) for the
> phased path to live use. No track-record claims are made anywhere in this
> repo — findings stand on their own executed PoCs.

## What's in the box

| Path | What it is |
|---|---|
| `agent/audithawk.ts` | The agent definition (system prompt + docs) for the Forge harness |
| `tools/` | Audit toolbelt: `slither_scan`, `forge_test`, `rag_search_findings`, `fetch_bounty` (Browserbase) |
| `ml/` | Dataset ingestion + retrieval over real audit findings (HF `Zaevlad/audit-findings-dataset`, your own public reports) |
| `infra/` | Docker: Foundry + Slither sandboxes (PoCs run here, not on your host) |
| `docs/BUILD_GUIDE.md` | **Start here** — phased build: environment → knowledge base → agent → live contest |
| `docs/AGENT_DESIGN.md` | Architecture: Karpathy-style agent principles, ml-intern patterns, PCHS sandboxing |
| `docs/ETHICS_AND_RULES.md` | Platform rules, AI-disclosure, what this agent will never do |
| `evals/` | Benchmark: held-out contests, findings rediscovered, PoC pass rate |

## 60-second orientation

```
bounty URL ──▶ ingest scope+repo ──▶ slither/aderyn ──▶ LLM review (RAG-grounded)
                                                            │
              submission draft ◀── report writer ◀── PoC loop (foundry test MUST pass)
                                                            │
                                   human review (Telegram approval) ──▶ submit
```

## Quickstart (after Build Guide Phase 0)

```bash
# 1. Knowledge base from real findings
cd ml && python ingest_dataset.py && python build_index.py

# 2. Tool sandboxes
cd ../infra && docker compose up -d

# 3. Run the agent inside Forge (see docs/BUILD_GUIDE.md Phase 3)
forge agent --agent audithawk "Work the contest at <url>: first-pass findings + PoCs"
```

## License

MIT for the code. The knowledge base is built from public audit reports and the
HF dataset under their own terms — see `docs/ETHICS_AND_RULES.md`.
