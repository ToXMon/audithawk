"""Query the findings index. Called by the rag_search_findings Forge tool.

Usage: python -m search_findings --query "..." --k 5
"""
import argparse, json, pickle
from rank_bm25 import BM25Okapi  # noqa: F401  (needed to unpickle)


def tokenize(s: str) -> list[str]:
    return [t for t in s.lower().replace("/", " ").replace("_", " ").split() if len(t) > 2]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--k", type=int, default=5)
    args = ap.parse_args()

    with open("data/index.pkl", "rb") as f:
        idx = pickle.load(f)
    bm25: BM25Okapi = idx["bm25"]
    rows = idx["rows"]

    scores = bm25.get_scores(tokenize(args.query))
    top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[: args.k]
    for rank, i in enumerate(top, 1):
        r = rows[i]
        print(f"### [{rank}] {r['title']}  ({r['severity']} · {r.get('contest','')})")
        print(f"source: {r['source']}")
        print(f"desc: {r['description'][:800]}")
        if r.get("poc_code"):
            print(f"poc: {r['poc_code'][:600]}")
        if r.get("fix"):
            print(f"fix: {r['fix'][:300]}")
        print()


if __name__ == "__main__":
    main()
