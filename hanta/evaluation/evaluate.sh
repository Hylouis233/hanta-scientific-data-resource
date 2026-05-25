#!/usr/bin/env bash
set -euo pipefail

CONFIG="${1:-configs/experiment.yaml}"
python evaluation/run_protocol.py "$CONFIG"
