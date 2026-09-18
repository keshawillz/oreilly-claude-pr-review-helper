#!/usr/bin/env bash
# Day 4: a style-only change plus one real bug. The nit gets dropped, the bug stays.
set -e
python src/review.py demos/diffs/day04.diff
echo
echo "To see the retry without spending tokens:"
echo "  terminal 1:  FAKE_CLAUDE_BAD_LINE=1 python tests/fake_claude.py"
echo "  terminal 2:  export the two variables it prints, then run this script again"
