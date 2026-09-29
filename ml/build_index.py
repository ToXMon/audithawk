"""Build a BM25 index over the findings corpus. Zero GPU, fully offline.

Usage: python build_index.py [--in data/findings.jsonl]
"""
import json, argparse, pickle
from rank_bm25 import BM25Okapi


def tokenize(s: str) -> list[str]:
    return [t for t in s.lower().replace("/", " ").replace("_", " ").split() if len(t) > 2]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="data/findings.jsonl")
    ap.add_argument("--min-quality", type=float, default=0.0,
                    help="Drop entries below this quality score (dataset ships one)")
    args = ap.parse_args()

    rows, docs = [], []
    with open(args.inp) as f:
        for line in f:
            r = json.loads(line)
            if r.get("quality") is not None and r["quality"] < args.min_quality:
                continue
            rows.append(r)
            docs.append(tokenize(" ".join(str(r.get(k, "")) for k in
                          ("title", "description", "poc_code", "fix"))))

    bm25 = BM25Okapi(docs)
    with open("data/index.pkl", "wb") as f:
        pickle.dump({"bm25": bm25, "rows": rows}, f)
    print(f"indexed {len(rows)} findings (of {len(rows)} after quality filter)")


if __name__ == "__main__":
    main()
