#!/usr/bin/env bash
# delivery-gate.sh — optional git pre-commit hook for the delivery-review-loop.
#
# Installs the mechanism-level enforcement: if a DELIVERY.md is staged for
# commit, it must contain the mandatory self-check block (contract / evidence /
# reviewer), or the commit is blocked.
#
# Install (from repo root):
#   cp hooks/delivery-gate.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# The hook is opt-in: if no DELIVERY.md is staged, it passes through silently.

set -euo pipefail

if git diff --cached --name-only | grep -qx "DELIVERY.md"; then
  if [ -f DELIVERY.md ]; then
    if ! python3 "$(git rev-parse --show-toplevel)/validate_delivery.py" DELIVERY.md --strict; then
      echo "pre-commit: DELIVERY.md is missing a complete self-check block." >&2
      echo "Add ① contract ② evidence ③ reviewer conclusion, then commit again." >&2
      exit 1
    fi
  fi
fi

exit 0
