#!/usr/bin/env bash
# Day 9: two reviews inside five minutes. First call writes the cache, second reads it.
set -e
echo "== First PR";  python src/reviewer.py demos/diffs/day06.diff --repo sample_app
echo; echo "== Second PR"; python src/reviewer.py demos/diffs/day07.diff --repo sample_app
echo; echo "Look at the 'cache write' and 'cache read' lines above."
