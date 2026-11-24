#!/usr/bin/env sh
set -eu

BASE_URL="${1:-http://localhost:8000}"
curl --fail --silent --show-error "${BASE_URL%/}/api/health" >/dev/null
printf 'Mig_Guard backend is warm at %s\n' "$BASE_URL"
