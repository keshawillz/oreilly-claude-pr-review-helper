#!/usr/bin/env bash
# Day 17: copy the Week 3 artifacts and the workflow into a checkout of oreilly-claude-review-target.
# Usage: demos/day17_install_into_target.sh ../oreilly-claude-review-target
set -e
target="$1"
mkdir -p "$target/.github/workflows" "$target/state"
cp -r .claude schemas prompts "$target/"
cp .github/workflows/review.yml "$target/.github/workflows/review.yml"
touch "$target/state/.gitkeep"
echo "Copied. In $target: commit, push, add the ANTHROPIC_API_KEY secret, install the Claude GitHub App."
