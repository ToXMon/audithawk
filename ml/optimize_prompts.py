"""AdalFlow-based prompt optimization for AuditHawk LLM nodes (L2).

Each llm node in machine/audit-graph.yaml has a versioned prompt in
ml/prompts/<prompt_id>.prompt.md. This script wraps a node as an AdalFlow
component and optimizes its prompt against mechanical eval metrics:

  reward = f(PoC pass rate, findings rediscovered, severity agreement, cost)

Promotion rule (see docs/MACHINE_ARCHITECTURE.md §3): an optimized prompt
replaces the current one only after beating it on the full held-out eval suite.
Every version + its scores is archived under ml/prompts/<id>/versions/.

Status: SKELETON. The crew fills in the AdalFlow wiring against the installed
version's API (pip install adalflow; docs: https://adalflow.sylph.ai) — core
concepts: Component / GradComponent for pipeline nodes, text-gradient and
few-shot-bootstrapping optimizers, and a Trainers loop driven by an eval fn.

Usage (after eval baseline exists):
    python optimize_prompts.py --node hypothesis --evals ../evals/results.json
"""
import argparse, json, shutil, sys
from datetime import datetime, timezone
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent / "prompts"

# Reward weights — tune with the human, then freeze per eval run.
REWARD_WEIGHTS = {
    "poc_pass_rate": 0.5,
    "findings_recall": 0.3,
    "severity_agreement": 0.15,
    "cost_penalty": 0.05,
}


def load_eval_scores(eval_path: Path) -> dict:
    """Load the metric dict produced by evals/score.py."""
    return json.loads(Path(eval_path).read_text())


def reward(scores: dict) -> float:
    """Mechanical reward — no vibes. Missing metrics score 0 and surface a warning."""
    total = 0.0
    for key, weight in REWARD_WEIGHTS.items():
        total += weight * float(scores.get(key, 0.0))
    return total


def archive_version(prompt_id: str, scores: dict) -> Path:
    """Snapshot the current prompt with its eval scores before optimization."""
    src = PROMPTS_DIR / f"{prompt_id}.prompt.md"
    versions = PROMPTS_DIR / prompt_id / "versions"
    versions.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    dest = versions / f"{stamp}-reward-{reward(scores):.3f}.md"
    shutil.copy(src, dest)
    return dest


def promote(prompt_id: str, candidate_text: str, baseline_reward: float, candidate_reward: float) -> Path:
    """Promote only on a strict eval win; archive the loser too."""
    assert candidate_reward > baseline_reward, "promotion requires beating the baseline"
    src = PROMPTS_DIR / f"{prompt_id}.prompt.md"
    versions = PROMPTS_DIR / prompt_id / "versions"
    versions.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    shutil.copy(src, versions / f"{stamp}-reward-{baseline_reward:.3f}-replaced.md")
    dest = versions / f"{stamp}-reward-{candidate_reward:.3f}-promoted.md"
    dest.write_text(candidate_text)
    src.write_text(candidate_text)
    return dest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", required=True, help="prompt_id, e.g. hypothesis, poc-engineer")
    ap.add_argument("--evals", required=True, help="evals/results.json from the held-out suite")
    ap.add_argument("--dry-run", action="store_true", help="score + archive only, no optimization")
    args = ap.parse_args()

    scores = load_eval_scores(Path(args.evals))
    baseline = reward(scores)
    archive_version(args.node, scores)
    print(f"node={args.node} baseline reward={baseline:.3f} (weights: {REWARD_WEIGHTS})")

    if args.dry_run:
        return

    # TODO(crew): AdalFlow wiring (see docs at https://adalflow.sylph.ai):
    #   1. Wrap the node as an adalflow Component whose `system_prompt` param
    #      loads from ml/prompts/<node>.prompt.md.
    #   2. Build the training set from eval transcripts: (scope+code surface ->
    #      expected finding structure) with the reward fn above as the metric.
    #   3. Run the optimizer (text-gradient / few-shot bootstrap) to propose
    #      candidate prompts.
    #   4. Re-run the held-out eval suite per candidate; call promote() only on
    #      a strict win. Log every run to evals/prompt-history.jsonl.
    print("optimization wiring is a crew task — see TODOs in this file", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
