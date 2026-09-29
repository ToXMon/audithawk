---
prompt_id: hypothesis
version: 1
node: hypothesize
changelog: v1 — extracted from agent/audithawk.ts; enforces corpus citations
---

For the given code surface (from static analysis + your reading), produce
vulnerability hypotheses.

For EACH hypothesis, output:
1. Pattern class (reentrancy, fee-accounting, ERC20-oddity, access-control,
   oracle, cross-chain, …)
2. Root cause: file, function, line — quote the code
3. Impact chain: who loses what, how much, under what conditions
4. Severity estimate per the platform's matrix
5. **Corpus citations**: run rag_search_findings on the pattern; cite the
   nearest neighbors (contest + finding id). A hypothesis with no corpus
   precedent AND no first-principles impact chain is `speculative` — it does
   not become a finding.
6. PoC plan: which foundry test would prove it (one paragraph)

Rules: maximum 5 PoC attempts will be spent on you — if the impact chain
doesn't survive your own scrutiny, don't propose it. No hypotheses about
out-of-scope code.
