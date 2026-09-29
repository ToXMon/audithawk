# AuditHawk Build Guide — from zero to live bounties

Phased. Each phase ends with something that works. Don't skip to Phase 5.

---

## Phase 0 — Environment (half a day)

**Host:** macOS (Apple Silicon) or Linux. 16GB+ RAM recommended.

```bash
# 1. Forge harness (the engine)
git clone https://github.com/ToXMon/forge && cd forge && npm install
cp .env.example .env   # fill FORGE_API_KEY (Venice/OpenRouter/etc.) — cheap open-weight models

# 2. AuditHawk (this repo, sibling directory)
git clone https://github.com/ToXMon/audithawk && cd ../audithawk

# 3. Solidity toolchain — inside Docker, never bare-metal (untrusted code!)
docker pull ghcr.io/foundry-rs/foundry:latest
docker pull trailofit/slither  # or build from infra/

# 4. Python for the knowledge base
cd ml && python3 -m venv .venv && source .venv/bin/activate
pip install datasets rank-bm25 pydantic  # BM25 first; embeddings later

# 5. Optional: Browserbase (headless browser for contest-platform pages)
# export BROWSERBASE_API_KEY=...   https://browserbase.com
```

**Smoke test:** `docker run --rm ghcr.io/foundry-rs/foundry:latest forge --version`

---

## Phase 1 — Knowledge base (1–2 days)

The agent's edge is grounding: every hypothesis gets compared against real
findings from real audits.

```bash
cd ml
python ingest_dataset.py          # pulls Zaevlad/audit-findings-dataset from HF
python ingest_reports.py /path/to/public-audits/reports/*.pdf   # third-party reference corpus
python build_index.py             # BM25 index (works offline, zero GPU)
python search_findings.py "execution fee hard-coded USDC decimals"   # try it
```

- `ingest_dataset.py` downloads the HF dataset and normalizes every entry to
  `{title, description, poc_code, fix, severity, quality, contest}`.
- Quality filter: entries carry a quality score — index only the top 60% for
  retrieval; keep all of it for eval.
- Third-party references — `Frankcastleauditor/public-audits` reports and any
  other public audit reports — get text-extracted (pypdf) and indexed under a
  `source: reference` tag with attribution. These are research references, NOT
  your findings; never represent them as personal track record. The corpus that
  makes the agent *yours* is built from your own accepted submissions over
  time.
- Upgrade path (Phase 6): swap BM25 → embeddings (open-weight embedder via
  the same multi-provider routing), then SFT.

---

## Phase 2 — Tool sandboxes (1 day)

`infra/docker-compose.yml` runs two services:

- **foundry**: where every PoC compiles and runs (`forge test`). The agent may
  only touch `/workdir` mounts — one workspace per audit session.
- **slither**: static analysis over a mounted target repo.

Nothing the agent reviews ever executes on the host. See
`docs/AGENT_DESIGN.md` §Sandboxing for the PCHS hardening path (gVisor →
Firecracker) before any multi-tenant use.

---

## Phase 3 — The agent (2–3 days)

1. Copy `agent/` + `tools/` into the forge tree (or add as a workspace package —
   `forge/src/agents/audithawk.ts` re-exports from this repo).
2. Register the tools in `forge/src/tools/index.ts` (they implement Forge's
   `ToolSpec`: name, zod schema, async handler).
3. Add the agent definition to `forge/src/server/index.ts` next to
   `fullstackAgent()`.
4. Wire the knowledge base: `rag_search_findings` shells out to
   `ml/search_findings.py` and returns formatted hits.

Then run your first session:

```
forge agent --agent audithawk \
  "Audit the repo at <git-url>. First-pass: static analysis + top-5 hypotheses
   with severity estimates. No PoCs yet."
```

Read every line the agent produces. Your review IS the training signal.

---

## Phase 4 — The PoC loop (2–3 days, the hard part)

A finding without an executed PoC is worth zero in contests. The gate:

```
hypothesis ──▶ agent writes foundry test ──▶ forge test (in container)
     ▲                                              │
     └──────────── fail → revise hypothesis ◀───────┘
```

- Tool `forge_test` mounts the session workspace, runs `forge test -vvv`,
  returns pass/fail + traces.
- The agent's system prompt **forbids** reporting a finding whose PoC didn't
  execute (see `agent/audithawk.ts` — this is enforced in the prompt AND by
  the tool refusing to mark `proven: true` without a green test).
- Doom-loop guard: max 5 PoC attempts per hypothesis, then drop it (ml-intern
  pattern; Forge's `maxSteps` + your review handle the rest).

---

## Phase 5 — Live: your first contest (ongoing)

1. **Pick a platform you've read the rules of.** AI-assistance terms differ
   (`docs/ETHICS_AND_RULES.md`); C4/Sherlock/Cantina contests are the safest
   start — public repos, fixed windows, clear judges.
2. **Week 1 ritual:** agent first-pass → you verify each finding by hand →
   submit only what you'd sign your handle to. Log everything in `evals/`.
3. **Escalation path:** contests → private client work → Immunefi live
   bounties (highest payouts, highest bar — the PoC gate matters most here).
4. **Track:** findings submitted / accepted / paid. That ratio is your real
   benchmark, and it becomes the agent's eval target.

**Money expectations, honestly:** first contests may net $0. The corpus and
the loop compound — most successful AI-leveraged auditors report the agent
finding ~30–50% of their medium-severity surface, with humans finding the
highs. Budget 6–8 weeks before income is meaningful.

---

## Phase 6 — ML upgrades (when Phase 5 pays)

1. Embeddings for retrieval (open-weight embedder, routed like your LLMs).
2. SFT on (context → finding+PoC+severity) from the top-quality half of the
   corpus. Eval on held-out contests *before* trusting the fine-tune.
3. Private corpus growth: every accepted submission (after embargo) becomes a
   new training row. This is the compounding moat.
