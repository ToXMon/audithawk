# Ethics, platform rules, and hard lines

## Non-negotiables

1. **You submit; the agent drafts.** The human makes every submission decision
   and every severity call that ships under their handle.
2. **No fabricated credentials, anywhere.** Reports, READMEs, and outreach
   materials in this ecosystem must never claim audits, placements, or client
   relationships that aren't verifiable. The security community cross-checks
   leaderboard handles fast, and a manufactured track record is the fastest
   way to end a career in this industry. Track record = what the platforms can
   confirm, full stop.
3. **Responsible disclosure only.** No exploiting live protocols outside an
   authorized bounty scope. No testing on mainnet without written program
   authorization. The PoC gate exists partly for this: a proven PoC against a
   forked/testnet state is evidence; a mainnet exploit is a crime.
4. **AI disclosure.** Platform rules on AI-assisted findings differ and change.
   Before submitting to any platform, read its current terms. Disclose where
   required. If a platform bans AI assistance, don't use it there.

## Platform notes (verify current terms before relying on this)

| Platform | Format | Notes to verify yourself |
|---|---|---|
| Code4rena | Contests | Public repos, fixed windows, judge-graded |
| Sherlock | Contests | Stricter PoC requirements |
| Cantina | Contests + private | Mixed model |
| Immunefi | Live bounties | Highest payouts; highest bar for PoC + impact proof |
| Hacken (HackenProof) | Bounties | Read per-program scope |

## Licenses

- Code in this repo: MIT.
- `Zaevlad/audit-findings-dataset`: check the HF dataset card for license terms
  before any commercial use. Fine for personal research/RAG.
- Public audit reports (`Frankcastleauditor/public-audits` is a third-party
  reference — NOT authored by this project; C4/Sherlock public reports, etc.):
  index for personal research with attribution. Don't republish others' reports
  in a product. Don't imply authorship of any third-party finding.
