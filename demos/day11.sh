#!/usr/bin/env bash
# Day 11: interactive to headless. Run the steps one at a time during the session.

# macOS has no timeout command. After `brew install coreutils`, gtimeout stands in for it.
if ! command -v timeout >/dev/null 2>&1; then timeout() { gtimeout "$@"; }; fi

# 0. Something to review: the Day 7 diff, staged into sample_app (skipped if it already has changes)
git diff --quiet -- sample_app && git apply -p1 --directory=sample_app demos/diffs/day07.diff

# 1. Interactive: opens a session and waits for you
# claude "Review my uncommitted changes"

# 2. Same call from a script: nobody answers, so it hangs
timeout 5 claude "Review my uncommitted changes"
echo "exit code: $?"            # 124 = timeout had to kill it

# 3. Print mode: runs, prints, exits
git diff | claude -p "Review this diff for bugs"
echo "exit code: $?"            # 0 on success

# 4. Same behavior on every machine, model pinned
# export ANTHROPIC_API_KEY="..."  # bare mode skips your login
git diff | claude --bare -p "Review this diff for bugs" \
  --model claude-sonnet-5

# Local debugging only. Commented out because each one reopens an interactive
# session and waits for you, like step 1. CI never uses them: every run starts
# clean, so one pull request's review can't leak into the next.
# claude -c          # continue the most recent conversation here
# claude -r "day11"  # resume a session by name or ID

# Done? Put sample_app back:  git checkout -- sample_app
