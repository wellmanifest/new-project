#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 "$repo_root/tests/scaffold_bootstrap_test.py" FreshBootstrapTest

if [[ -f "$repo_root/tests/bootstrap_adoption_split_test.py" ]]; then
  python3 -B "$repo_root/tests/bootstrap_adoption_split_test.py"
fi
