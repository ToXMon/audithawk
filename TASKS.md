# TASKS.md — milestone board for the autonomous crew

Work top-down. A milestone is done only when its **verification** passes.
Tick with `[x]`, note the commit hash.

---

## M1 — Environment boots (env)
- [ ] `docker run --rm ghcr.io/foundry-rs/foundry:latest forge --version` prints a version
- [ ] `cd ml && pip install -r requirements.txt` succeeds
- [ ] Forge harness runs: `cd ../forge && npm test` passes
**Verify:** `bash evals/verify/m1.sh` (all three checks)

## M2 — Knowledge base live (corpus)
- [ ] `python ml/ingest_dataset.py` writes `ml/data/findings.jsonl` (>1000 rows)
- [ ] `python ml/build_index.py` builds `ml/data/index.pkl`
- [ ] `python ml/search_findings.py --query "hard-coded fee assumes USDC decimals" --k 3` returns ≥1 relevant hit
- [ ] `python ml/ingest_reports.py <path-to-public-audits>/reports/*.pdf` indexes reference corpus (tagged `source: reference`)
**Verify:** `bash evals/verify/m2.sh`

## M3 — Sandboxes + first PoC (proof loop)
- [ ] `infra/docker-compose.yml` up; foundry container runs a hello-world forge test
- [ ] `forge_test` tool executes a sample PoC inside the container and returns PROVEN true/false correctly (test both paths with a deliberately-failing PoC)
**Verify:** `bash evals/verify/m3.sh`

## M4 — Agent wired into Forge (agent)
- [ ] `audithawkAgent()` + audit tools registered in Forge; `forge --help`/agent list shows audithawk
- [ ] End-to-end on a toy repo: agent runs slither_scan → rag_search_findings → writes a foundry PoC → forge_test marks it proven (toy repo: a contract with a known reentrancy bug)
**Verify:** session transcript + `PROVEN: true` in workspace; commit the transcript to `evals/transcripts/`

## M5 — Evals baseline (evals)
- [ ] One held-out contest ingested (report NOT in RAG index)
- [ ] Agent first-pass run logged to `evals/transcripts/`; findings-rediscovered + PoC-validity numbers written to `evals/results.json`
- [ ] Numbers committed with the prompt version used
**Verify:** `python evals/score.py evals/results.json` prints the metric table

## M6 — Remote build box (infra, needs human: funded Akash/Brev)
- [ ] Forge server + scanner deployed to Akash (reuse forge `deploy/`)
- [ ] OR GPU box (brev.dev) for Phase 6 SFT — **human approval required first**
**Verify:** public URL returns `/health` ok / GPU job completes

## M7 — Live contest support (with human)
- [ ] Human picks a live contest; agent produces first-pass findings + PoCs
- [ ] Human reviews; accepted/rejected logged in `evals/log.jsonl`
**Verify:** `evals/log.jsonl` entry with real outcome
