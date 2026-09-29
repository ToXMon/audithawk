# AuditHawk evals

**Rule: no prompt/tool change ships without a before/after on this suite.**

## Benchmark design

- **Held-out contests:** pick 3 past Code4rena/Sherlock contests whose full
  reports are public. Hold out entirely (never indexed in RAG). Re-index when
  refreshing the benchmark so the agent can't have seen them.
- **Metrics:**
  1. Findings rediscovered / total judge-confirmed findings (recall)
  2. Severity agreement (your severity vs judges')
  3. PoC validity rate (executed green / PoCs attempted)
  4. False-positive rate (agent findings judges rejected)
  5. Cost per contest (from Forge `llm_usage` stats — token accounting exists)
- **Cadence:** run after every corpus change, prompt change, or model change.

## Practical target ladder

| Stage | Target |
|---|---|
| RAG baseline | ≥30% medium-severity recall, >60% PoC validity |
| After SFT | ≥50% medium recall, >70% PoC validity |
| Live-ready | Human-review-to-submission time < 2× manual, ≥1 accepted finding per contest |

## Logging

Every live session appends to `evals/log.jsonl`:
`{contest, findings_submitted, accepted, paid_usd, agent_findings_used, human_overrides}`.
The paid/accepted ratio is the number that tells you if this works.
