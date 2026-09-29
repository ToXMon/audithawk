"""Ingest the HF audit-findings dataset into a normalized JSONL corpus.

Every entry becomes: {id, contest, title, description, poc_code, fix, severity, quality}
Usage: python ingest_dataset.py [--dataset Zaevlad/audit-findings-dataset] [--out data/findings.jsonl]
"""
import argparse, json, re
from datasets import load_dataset

SEVERITY_RE = re.compile(r"\b(High|Medium|Low|Critical|Undetermined)\b", re.I)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="Zaevlad/audit-findings-dataset")
    ap.add_argument("--out", default="data/findings.jsonl")
    args = ap.parse_args()

    ds = load_dataset(args.dataset)
    rows = ds["train"] if "train" in ds else list(ds.values())[0]

    seen = 0
    with open(args.out, "w") as f:
        for i, row in enumerate(rows):
            text = json.dumps(row, default=str)
            # The dataset is semi-structured; extract what we can defensively.
            entry = {
                "id": row.get("id", i),
                "contest": row.get("contest", row.get("source", "")),
                "title": (row.get("title") or "")[:200],
                "description": (row.get("description") or row.get("issue") or "")[:4000],
                "poc_code": (row.get("poc") or row.get("code") or "")[:8000],
                "fix": (row.get("recommendation") or row.get("fix") or "")[:2000],
                "severity": next(SEVERITY_RE.finditer(text), None).group(0).title()
                    if SEVERITY_RE.search(text) else "Unknown",
                "quality": float(row["quality"]) if row.get("quality") else None,
                "source": "hf:" + args.dataset,
            }
            f.write(json.dumps(entry) + "\n")
            seen += 1
    print(f"wrote {seen} findings → {args.out}")


if __name__ == "__main__":
    main()
