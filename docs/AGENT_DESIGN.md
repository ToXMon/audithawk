# AuditHawk Agent Design

Principles first, architecture second, code last. Read top to bottom.

## 1. Agent principles (the Karpathy school)

From Karpathy's agent engineering talks and practice, applied here:

1. **The loop is simple; the tools do the work.** The agent loop is: LLM call →
   tool calls → results → repeat. All intelligence lives in (a) tool design and
   (b) context curation — not in prompt tricks.
2. **Evals before autonomy.** No phase of this agent gets more freedom until it
   scores on a held-out benchmark (`evals/`). Autonomy is *earned per-capability*.
3. **Keep the model on a leash.** Deterministic scaffolding (slither, foundry,
   the filesystem) does the deterministic parts. The LLM only does the part
   that needs judgment: pattern hypotheses, impact reasoning, report prose.
4. **Vibe-coding the agent is how it dies.** Every prompt change ships with a
   before/after eval. This is the same discipline as any production system.
5. **Small models + great tools beat big models + vague tools.** Slither finds
   the candidate surfaces for free; the LLM reasons only about those.

## 2. Inherited patterns (from HF ml-intern, archived)

ml-intern's architecture is the best public blueprint for a serious agent CLI.
What we take, and where it lives in Forge:

| ml-intern pattern | AuditHawk / Forge home |
|---|---|
| Agentic loop w/ max iterations | `forge/src/harness/loop.ts` (exists) |
| Doom-loop detector (repeated tool calls) | Forge `maxSteps` + new `maxPocAttempts` per hypothesis in `forge_test` |
| Approval gates for dangerous ops | Forge `PolicyGuard` + Telegram/UI approvals (exists) |
| LiteLLM multi-provider, local models | Forge `ProviderRegistry` (Venice/Surplus/AkashML/Ollama — exists) |
| Sandbox tool runtime | `infra/` Docker + PCHS hardening path |
| Session traces to HF dataset | Forge event log (`llm_usage` events, workspaces) — your private corpus grows automatically |

## 3. Architecture

```
                    ┌──────────────────────────────────────────┐
                    │            Forge harness (exists)         │
                    │   loop · checkpoints · approvals · stats  │
                    └───────────────┬──────────────────────────┘
                                    │ AgentDefinition + ToolSpecs
        ┌───────────────────────────┼────────────────────────────┐
        │                      AuditHawk                         │
        │                                                        │
  Ingest tools           Review loop               Proof loop     │
  ┌─────────────┐   ┌───────────────────┐   ┌──────────────────┐ │
  │fetch_bounty │──▶│ slither/aderyn    │──▶│ forge_test       │ │
  │(Browserbase)│   │ rag_search_       │   │ (Docker foundry) │ │
  │git_clone    │   │  findings (BM25)  │   │ PoC MUST pass    │ │
  └─────────────┘   │ LLM hypothesis    │   └──────────────────┘ │
                    └───────────────────┘                         │
                                    │                             │
                          report writer (platform format)        │
                                    │                             │
                          human approval (Telegram) ──▶ submit    │
                    └──────────────────────────────────────────┘
```

### The three loops, explicitly

1. **Ingest** (deterministic): fetch scope/rules/repo/docs. Browserbase for
   JS-heavy contest pages; plain git for code. Output: `scope.json` + cloned repo.
2. **Review** (judgment): static analysis output + RAG hits → LLM hypothesizes
   vulnerabilities with severity estimates. Every hypothesis cites its nearest
   corpus neighbors ("this matches maia_H-04 gas-accounting pattern") —
   citations force the model to be specific and give you something to verify.
3. **Proof** (deterministic gate): a hypothesis isn't a finding until a Foundry
   test executes green in the container — `forge test` against an **anvil fork**
   of the relevant chain state for realistic conditions. The tool, not the
   prompt, is the source of truth for `proven: true`.

### Verification stack — what proves what (read this before wiring tools)

| Claim | Proven by | NOT proven by |
|---|---|---|
| "The PoC exploits the bug" | `forge test` green in the foundry container (deterministic, replayable) | any browser |
| "The exploit works against realistic state" | `forge test` against an **anvil fork** of live chain state | any browser |
| "The bug is visible on the protocol's frontend" | **Browserbase session replay** driving the testnet frontend (screenshot/replay as evidence artifact) | — |
| "The submission page renders / contest state is X" | Browserbase fetch/browsers | — |

Browserbase is the **web interaction layer**, not a compute sandbox: it cannot
compile or run Solidity. Its agentic value is (a) ingest of JS-heavy contest
pages, (b) recorded visual evidence of UI-exploitable bugs via Stagehand-driven
sessions (Live View replays make the PoC *accessible* to non-technical judges),
and (c) read-only platform monitoring. PoC execution proof always comes from
the foundry container.

### The human's role (non-negotiable)

The agent is a **first-pass analyst**, not an auditor. You read every finding,
re-derive the impact, and decide what ships under your handle. Every
accept/reject you make is logged and becomes eval + corpus data.

## 4. Sandboxing (PCHS hardening path)

| Stage | Isolation | When |
|---|---|---|
| 1. Docker (now) | Namespaced FS, no network for foundry except RPC pinning | personal use |
| 2. gVisor (runsc) | Syscall interception | before sharing workspaces |
| 3. Firecracker microVM | Full VM boundary | multi-tenant product |

Target repos are **adversarial inputs**. Assume any contract you audit is
trying to exploit your tooling. Never run `forge script` against live keys;
never mount host credentials into the container.

## 5. What we deliberately did NOT build

- A custom agent runtime (Forge's loop is sufficient — avoid NIH).
- Vector DB infra (BM25 first; add embeddings only when BM25 recall measurably
  limits findings).
- Auto-submission to platforms. The human clicks submit — always.
