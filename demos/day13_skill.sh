#!/usr/bin/env bash
# Day 13: run the Skill headless. Then edit a severity line in .claude/CLAUDE.md and run it again.
set -e
cd "$(dirname "$0")/.."      # the helper repo root, wherever you ran this from

# 0. A project for the Skill to review. CLAUDE.md says the code lives in app/ and the tests in
#    tests/, and that is true inside sample_app. So give sample_app the Skill and CLAUDE.md
#    (a fresh copy each run, so edits to .claude/CLAUDE.md at the repo root count), and stage
#    the Day 4 diff (skipped if sample_app already has changes).
rm -rf sample_app/.claude && cp -R .claude sample_app/.claude
git diff --quiet -- sample_app && git apply -p1 --directory=sample_app demos/diffs/day04.diff

# 1. Run the Skill from inside sample_app. --relative makes the diff paths read app/orders.py,
#    the way CI will see them on Day 17.
cd sample_app
git diff --relative | claude -p "/pr-review" \
  --output-format json \
  --json-schema "$(cat ../schemas/findings.json)" \
  | jq '.structured_output.findings[] | {severity, file, line, issue}'

# Done? Put it all back:  git checkout -- .claude sample_app && rm -rf sample_app/.claude
