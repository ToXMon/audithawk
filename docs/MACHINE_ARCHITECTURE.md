# AuditHawk Machine Architecture — graphs, loops, and prompt optimization

**The honest answer to "is this multi-agent orchestration?":** not yet, and not
by default. Today it is **one agent loop over an explicit pipeline graph** —
mostly deterministic tool nodes with LLM judgment at specific nodes. This doc
defines the machine architecture so every builder agent (pi, firstmate) builds
the same machine, and defines the ladder from single-agent to multi-agent.

---

## 1. The ladder — levels of agency

| Level | Shape | When |
|---|---|---|
| **L0** | Single agent loop + tools (Forge harness today) | now — `agent/audithawk.ts` |
| **L1** | Explicit pipeline graph: nodes declared, typed, machine-readable (`audit-graph.yaml`) | build next |
| **L2** | Per-node prompt optimization: prompts are versioned artifacts, optimized offline by **AdalFlow** against eval metrics | after M5 evals baseline |
| **L3** | Node promotion to sub-agents where *context isolation* or *parallelism* demands | only with eval evidence |

**Rule: autonomy and decomposition are earned by evals, not assumed.** A node
stays an LLM call inside one loop until its context overflows or it needs
independent tool access — then it promotes to a sub-agent (L3) with its own
Forge session. This is the evals-first discipline: the graph makes promotion
mechanical instead of vibes-based.

## 2. The graph (`machine/audit-graph.yaml`)

The canonical machine definition. Node types:

- `tool` — deterministic execution (slither_scan, forge_test, git_clone)
- `llm` — judgment node, carries a `prompt_id` into the versioned registry
- `gate` — hard pass/fail that blocks progression (PoC must run green)
- `human` — approval stop (Telegram/UI); nothing bypasses it
- `rag` — deterministic retrieval over the findings corpus

```yaml
graph: audithawk-v1
entry: ingest
nodes:
  ingest:        {type: tool,     tool: fetch_bounty + git_clone / audit-repo-cloner}
  scope:         {type: llm,      prompt_id: scope-parse}        # scope.json + checklist subset selection
  static_scan:   {type: tool,     tool: slither_scan | aderyn_scan}
  hypothesize:   {type: llm,      prompt_id: hypothesis, loop: {max: 5, per: checklist-category}}
  ground:        {type: rag,      tool: rag_search_findings}     # citation required
  write_poc:     {type: llm,      prompt_id: poc-engineer}
  run_poc:       {type: gate,     tool: forge_test, on_fail: {revise: write_poc, max_attempts: 5}}
  draft_report:  {type: llm,      prompt_id: report-writer, format: cyfrin/report-generator-template}
  human_review:  {type: human}
edges:
  ingest -> scope -> static_scan -> hypothesize -> ground -> write_poc -> run_poc
  run_poc(green) -> draft_report -> human_review
  run_poc(red, attempts<5) -> write_poc
  run_poc(red, attempts>=5) -> drop_hypothesis -> hypothesize
parallelizable: [hypothesize]   # per checklist category — the L3 seam
```

## 3. Prompt registry + AdalFlow (L2)

**Every `llm` node's prompt is a versioned artifact, never inline.**

```
ml/prompts/
  hypothesis.prompt.md      # v3 — changelog in frontmatter
  poc-engineer.prompt.md
  report-writer.prompt.md
  scope-parse.prompt.md
```

- Forge loads prompt versions at session start (prompt_id → file → content).
- **AdalFlow is the offline optimizer** (`ml/optimize_prompts.py`, Python — the
  ML side of this project is already Python). Each LLM node is wrapped as an
  AdalFlow `Component`; the optimizer (text-gradient / few-shot bootstrapping)
  proposes prompt variants.
- **The reward signal is mechanical, not vibes:** on held-out contest evals —
  PoC pass rate (forge_test), findings rediscovered vs judge-confirmed ground
  truth, severity agreement, cost per finding (Forge `llm_usage` events).
- **Promotion rule:** an optimized prompt replaces the current one only after
  beating it on the full held-out suite. Every version keeps its eval scores
  (`ml/prompts/<id>/versions/`), so regressions are revertible — the same
  evals-first discipline as everything else in this repo.

Why AdalFlow and not a homegrown tuner: it gives the text-gradient + bootstrap
machinery, dataset/eval plumbing, and traceability for free — prompt
optimization is a solved problem and our edge is the domain reward signal
(PoC validity), not the optimizer.

## 4. Multi-agent promotion criteria (L3)

Promote a node to a sub-agent ONLY when one holds:

1. **Context overflow:** the node's working set (checklist category + relevant
   code + corpus hits) no longer fits its share of the context window.
2. **Independent tool access:** the node needs tools the main loop shouldn't
   hold (e.g., a Browserbase session driver).
3. **Parallelism:** `hypothesize` per checklist category can fan out —
   13 categories = 13 scoping-bounded hypothesis streams, merged before PoC.

L3 candidates in priority order: (a) per-category hypothesis sub-agents,
(b) PoC engineer (owns the foundry workspace), (c) report writer.
The orchestrator remains Forge's loop; sub-agents are Forge sessions launched
as tools, so approvals/checkpoints/usage accounting apply unchanged.

## 5. What pi/firstmate build from this

- `machine/audit-graph.yaml` is the contract: implement nodes as functions
  with the declared types, edges, and loop policies. No hidden stages.
- Extract the three prompts from `agent/audithawk.ts` into the registry
  (`ml/prompts/`) and make Forge load them by id.
- Implement `ml/optimize_prompts.py` against the eval harness (AdalFlow in
  `ml/requirements.txt`).
- Wire `ml/optimize_prompts.py` into `TASKS.md` M5: the eval baseline is what
  the optimizer optimizes against.
