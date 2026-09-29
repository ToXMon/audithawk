"""Ingest your own public audit report PDFs into the corpus.

Usage: python ingest_reports.py /path/to/public-audits/reports/*.pdf
"""
import glob, json, sys
from pypdf import PdfReader


def main() -> None:
    out = "data/findings.jsonl"
    n = 0
    with open(out, "a") as f:
        for path in sys.argv[1:]:
            reader = PdfReader(path)
            text = "\n".join(p.extract_text() or "" for p in reader.pages)
            # A full report is one document with many findings; index it in
            # coarse chunks so retrieval can hit specific findings.
            for chunk_i, chunk in enumerate(_chunks(text, 6000)):
                f.write(json.dumps({
                    "id": f"{path.split('/')[-1]}#{chunk_i}",
                    "contest": path.split("/")[-1],
                    "title": path.split("/")[-1].replace(".pdf", ""),
                    "description": chunk[:6000],
                    "poc_code": "",
                    "fix": "",
                    "severity": "Report",
                    "quality": None,
                    "source": "personal",
                }) + "\n")
                n += 1
    print(f"appended {n} chunks from {len(sys.argv)-1} PDFs → {out}")


def _chunks(s: str, size: int):
    for i in range(0, len(s), size):
        yield s[i : i + size]


if __name__ == "__main__":
    main()
