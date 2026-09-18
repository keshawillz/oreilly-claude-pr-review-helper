#!/usr/bin/env bash
# Day 5: golden-set run one. Write the score in row one of the scoreboard.
set -e
python src/review.py demos/diffs/day04.diff
echo; python eval/run_golden.py --reviewer week1
