#!/usr/bin/env bash
# Day 16: two invocations, no shared session. Live generation, so results vary between runs.

# Session A: the writer
claude -p "Add a small in-memory rate limiter to sample_app/app/auth.py: \
at most 5 login attempts per email per minute." \
  --permission-mode acceptEdits

# Ask session A to grade its own work. -c continues the same session.
claude -p -c "Review the change you just made. Any bugs?"

# Session B: the reviewer. New process, no memory of session A.
git diff | claude -p "Review this diff. Return findings only." \
  --append-system-prompt-file prompts/reviewer.md \
  --output-format json \
  --json-schema "$(cat schemas/findings.json)" \
  --no-session-persistence \
  | jq '.structured_output.findings'

git checkout -- sample_app     # put the sample app back
