#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
. .venv/bin/activate
PYTHONPATH=. python -m src.main --config configs/groups.yaml
