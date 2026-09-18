#!/usr/bin/env bash
# Day 12: the same command, headless, with a contract.
set -e

# 0. Something to review: the Day 7 diff, staged into sample_app (skipped if it already has changes)
git diff --quiet -- sample_app && git apply -p1 --directory=sample_app demos/diffs/day07.diff
claude -p "/review-diff" \
  --output-format json \
  --json-schema "$(cat schemas/findings.json)" \
  | tee /tmp/envelope.json | jq '{session_id, total_cost_usd, is_error}'
echo "== The findings live under structured_output"
jq '.structured_output.findings' /tmp/envelope.json
# Debugging a run that surprised you? Watch the events as they happen:
# claude -p "/review-diff" --output-format stream-json --verbose

# Done? Put sample_app back:  git checkout -- sample_app
