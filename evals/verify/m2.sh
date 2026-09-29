#!/usr/bin/env bash
# M2 verification: knowledge base live
set -e
LINES=$(wc -l < ml/data/findings.jsonl)
[ "$LINES" -gt 1000 ] && echo "✓ corpus: $LINES findings" || { echo "✗ corpus too small: $LINES"; exit 1; }
test -f ml/data/index.pkl && echo "✓ index built"
cd ml && python3 -m search_findings --query "hard-coded fee assumes USDC decimals" --k 3 | grep -q "###" && echo "✓ retrieval works"
