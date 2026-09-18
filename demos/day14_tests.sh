#!/usr/bin/env bash
# Day 14: test suggestions that fill gaps.
set -e
cd "$(dirname "$0")/.."      # the helper repo root, wherever you ran this from

# 0. Same setup as Day 13: sample_app gets the Skill and CLAUDE.md, and the Day 7 diff is staged
#    (skipped if sample_app already has changes). The Skill reads tests/ and tests/fixtures/ in there.
rm -rf sample_app/.claude && cp -R .claude sample_app/.claude
git diff --quiet -- sample_app && git apply -p1 --directory=sample_app demos/diffs/day07.diff

# 1. Run the Skill from inside sample_app and print only the test suggestions
cd sample_app
git diff --relative | claude -p "/pr-review" \
  --output-format json \
  --json-schema "$(cat ../schemas/findings.json)" \
  | jq '.structured_output.suggested_tests'

# Done? Put it all back:  git checkout -- .claude sample_app && rm -rf sample_app/.claude
