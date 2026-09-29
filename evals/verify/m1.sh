#!/usr/bin/env bash
# M1 verification: environment boots
set -e
docker run --rm ghcr.io/foundry-rs/foundry:latest forge --version | grep -q forge && echo "✓ foundry"
test -f ml/requirements.txt && (cd ml && python3 -c "import datasets, rank_bm25, pypdf" 2>/dev/null && echo "✓ python deps") || echo "✗ python deps missing"
(cd ../forge && npm test --silent > /dev/null 2>&1 && echo "✓ forge harness") || echo "✗ forge harness"
