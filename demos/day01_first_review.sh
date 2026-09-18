#!/usr/bin/env bash
# Day 1: first review. Run from the repo root at tag day-01.
set -e
echo "== 1. The first review"
python src/review.py demos/diffs/day01.diff
if grep -q "max_tokens=1024" src/review.py; then
  echo; echo "== 2. Starve it: max_tokens=60. Watch stop_reason change."
  sed 's/max_tokens=1024/max_tokens=60/' src/review.py > /tmp/review_60.py
  python /tmp/review_60.py demos/diffs/day01.diff
fi
echo; echo "Next: edit the model name in src/review.py to claude-haiku-4-5 and run it again."
