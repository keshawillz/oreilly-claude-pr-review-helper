#!/usr/bin/env bash
# Day 3: the rubric is the only thing that changed since yesterday.
set -e
echo "== The rubric"; cat prompts/review_system.md
echo; echo "== The review, with the rubric as the system prompt"
python src/review.py demos/diffs/day01.diff
echo; echo "Compare with yesterday: git stash or check out day-02 and run the same diff."
