#!/usr/bin/env bash
set -euo pipefail

CONFIG="${1:-configs/experiment.yaml}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
python "$PROJECT_ROOT/evaluation/run_protocol.py" "$CONFIG"
