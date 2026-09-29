#!/usr/bin/env bash
# M3 verification: sandbox PoC loop — run a passing and a failing foundry test in the container
set -e
cd infra && docker compose up -d
echo "→ run a real PoC through the forge_test tool path and check PROVEN lines"
echo "  (wired in M4; until then this checks the compose stack is up)"
docker compose ps | grep -q foundry && echo "✓ foundry sandbox up"
