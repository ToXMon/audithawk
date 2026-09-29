---
prompt_id: scope-parse
version: 1
node: scope
changelog: v1 — extracted from agent/audithawk.ts operating contract
---

Parse the ingested contest/bounty materials into `scope.json`.

Output, exactly:
1. `in_scope`: files/contracts/directories in scope, verbatim from the source
2. `out_of_scope`: everything explicitly excluded
3. `severity_matrix`: the platform's severity definitions, quoted
4. `checklist_categories`: which of the 13 checklist categories apply to this
   target (Solidity/EVM vs Solana/Rust vs cross-chain) — load only these
   category files from references/checklist/
5. `deadlines` and `prize_structure`

If scope is ambiguous, STOP and ask. Never analyze out-of-scope code — flag
the ambiguity instead.
