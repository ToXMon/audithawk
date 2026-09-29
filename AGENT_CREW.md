# AGENT_CREW.md — operating contract for autonomous builders

**Who this is for:** coding agents (pi, firstmate, AdaL, Claude Code, …) tasked
with building AuditHawk without a human in the loop for most steps.
**The human's role:** fund accounts, approve escalations, make security judgment
calls, and click "submit" on any finding.

## 1. Ground rules for autonomous work

1. **One milestone at a time, top of `TASKS.md`.** Do not start a milestone
   until the previous one's *verification command* passes.
2. **Every milestone has a machine check.** A task without a runnable
   verification is not done — "it should work" does not count.
3. **Commits are cheap.** Commit after every verification. Branch per milestone:
   `milestone/M1-env`, `milestone/M2-corpus`, …
4. **Never touch:** live keys outside `.env`, anything outside this repo +
   declared sibling clones, network egress from foundry containers except an
   explicitly pinned RPC, and any submission flow to a bounty platform.
5. **Escalate (stop and ask the human) when:** a milestone verification fails
   twice after real debugging; a step needs a funded purchase (> $5); a step
   touches platform TOS; a prompt/agent change would ship without an eval run.
6. **Cost discipline:** LLM calls go through Forge's ProviderRegistry on cheap
   open-weight models by default. Log spend per milestone. Brev.dev/Akash GPU
   only spins up for Phase 6 (SFT) with explicit human approval.

## 2. Tool inventory → what each is for

| Tool | Account needed | Used for | Notes |
|---|---|---|---|
| **Docker** | none (local) | Foundry/Slither sandboxes, all PoC execution | Phase 2 |
| **Forge harness** | LLM key (Venice/OpenRouter/…) | The agent runtime: loop, approvals, workspaces, token accounting | Already built |
| **HuggingFace** (`HF_TOKEN`) | free → pro | Dataset download (findings corpus), Inference Providers for open-weight models, trace datasets | Phase 1, 6 |
| **huggingface.co/chat** | free | Manual spot-checks of model behavior while building evals | optional |
| **Browserbase** | `BROWSERBASE_API_KEY` | Headless browsing of contest/bounty pages (JS-heavy) | `fetch_bounty` tool |
| **browser-use** (local) | none | Fallback + interactive verification of what pages render | dev tool |
| **Akash** (CLI / Console) | funded wallet | Hosting the scanner/agent server; later, GPU via providers | deploy/ scripts from Forge |
| **brev.dev** | funded account | GPU boxes for SFT fine-tuning (Phase 6 only) | do NOT start without human approval |
| **MCP access** | per-server | Ideabrowser (research, quota-limited), any security-data MCP servers added later | config pattern: `mcpServers` JSON |

## 3. Autonomous loop shape

```
read TASKS.md → claim top milestone → branch
  → implement → run verification command → pass?
       yes → commit + push + tick checkbox + next
       no  → debug (max 2 focused attempts)
              → still failing? write DEBUG_NOTES.md and STOP (escalate)
```

Context files every agent should read before starting: this file,
`TASKS.md`, `docs/BUILD_GUIDE.md`, `docs/AGENT_DESIGN.md`,
`docs/ETHICS_AND_RULES.md`.

## 4. What agents must never do autonomously

- Submit anything to a bounty/contest platform.
- Claim findings, authorship, or track record (see ETHICS_AND_RULES §2).
- Spin up paid GPU (brev.dev) or close Akash leases above the human-set cap.
- Modify `docs/ETHICS_AND_RULES.md` — changes require the human.
- Push to `main` directly after M3 (PRs + human merge from there on).
