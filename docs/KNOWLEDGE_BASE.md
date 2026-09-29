# Knowledge base — what to study and feed the agent

The agent's quality is capped by the corpus and by yours. Curated sources:

## Agent engineering (how to build it)

- **Andrej Karpathy** — agent-building philosophy this repo follows: simple
  loops, evals-first, tools over prompt tricks, "Software 3.0" framing.
  (His talks/notes are the reference; nothing here reinvents them.)
- **HF ml-intern** (archived, blueprint value): doom-loop detection, tool
  router design, LiteLLM multi-provider, trace datasets.

## Smart-contract security (what to audit and how)

- **Patrick Collins / Cyfrin** — Cyfrin Updraft courses: Solidity → Advanced
  Foundry → Security & Auditing. The free path from zero to contest-ready.
- **Cyfrin / CodeHawks** — audit methodology, public reports, first contests.
- **Solodit** (Cyfrin) — the searchable findings database; pairs with our RAG
  index (same idea, bigger corpus).
- **Blockchain Attack Vectors** materials and the classic reentrancy/oracle/
  access-control taxonomies — these are the pattern families our retrieval
  covers first.

## Ecosystem coverage (multi-platform)

| Platform | Language | Static tools | Note |
|---|---|---|---|
| Ethereum/EVM | Solidity | Slither, aderyn(EVM mode) | Default target |
| Solana/Anchor | Rust | aderyn, tractor? (verify) | Your strongest per your corpus |
| CosmWasm | Rust | cargo-audit + manual | Growing |
| Polkadot | Rust/ink! | manual + cargo | Niche |

> **On "Kun Chen":** I couldn't confidently map this name to a specific public
> body of work — point me at the exact resource (repo/course/lecture series)
> and I'll fold it into the corpus and this guide.

## Feeding the corpus

1. Public reports you contributed to (after embargo) — `ingest_reports.py`.
2. HF findings dataset — `ingest_dataset.py`.
3. Solodit exports (respect their ToS) for breadth.
4. Every session's accepted findings — the eval set becomes the corpus.
