#!/usr/bin/env bash
# Day 2: the same diff, now as JSON that matches schemas/findings.json.
set -e
echo "== The schema"; cat schemas/findings.json
echo; echo "== The structured review"
python src/review.py demos/diffs/day01.diff
