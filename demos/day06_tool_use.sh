#!/usr/bin/env bash
# Day 6: the bug depends on app/pricing.py, which the diff does not show.
set -e
echo "== Week 1 reviewer, diff only"; python src/review.py demos/diffs/day06.diff
echo; echo "== With get_file available"; python src/reviewer.py demos/diffs/day06.diff --repo sample_app
