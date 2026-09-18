#!/usr/bin/env bash
# Day 7: three tools. Watch the order Claude calls them in (printed on stderr).
set -e
python src/reviewer.py demos/diffs/day07.diff --repo sample_app
