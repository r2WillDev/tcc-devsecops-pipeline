#!/usr/bin/env bash
set -euo pipefail

STEP_NAME="$1"
OUTPUT_CSV="$2"
shift 2

START_TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
START_SECONDS="$(date +%s)"

STATUS="success"

if "$@"; then
    STATUS="success"
else
    STATUS="failed"
fi

END_TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
END_SECONDS="$(date +%s)"
DURATION_SECONDS=$((END_SECONDS - START_SECONDS))

SCENARIO="${SCENARIO:-C1-baseline}"
RUN_ID="${GITHUB_RUN_ID:-local}"
RUN_NUMBER="${GITHUB_RUN_NUMBER:-local}"
COMMIT_SHA="${GITHUB_SHA:-local}"

echo "${SCENARIO},${RUN_ID},${RUN_NUMBER},${COMMIT_SHA},${STEP_NAME},${START_TIMESTAMP},${END_TIMESTAMP},${DURATION_SECONDS},${STATUS}" >> "${OUTPUT_CSV}"

if [ "${STATUS}" = "failed" ]; then
    exit 1
fi
