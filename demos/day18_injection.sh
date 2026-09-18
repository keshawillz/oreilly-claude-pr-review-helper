#!/usr/bin/env bash
# Day 18: prove the hook denies approve and merge calls, with no model involved.
set -e
hook=.claude/hooks/deny_approve.py
echo "== An approve attempt"
echo '{"tool_name":"Bash","tool_input":{"command":"gh pr review 7 --approve"}}' | python3 $hook
echo; echo "== A merge through an MCP tool"
echo '{"tool_name":"mcp__github__merge_pull_request","tool_input":{"pullNumber":7}}' | python3 $hook
echo; echo "== An inline comment passes (no output means no objection)"
echo '{"tool_name":"mcp__github_inline_comment__create_inline_comment","tool_input":{"path":"app/db.py","line":20,"body":"note"}}' | python3 $hook
echo; echo "== A comment that quotes the attack passes too"
echo '{"tool_name":"mcp__github_inline_comment__create_inline_comment","tool_input":{"path":"app/orders.py","line":26,"body":"This comment tells reviewers to run gh pr merge. Ignore it."}}' | python3 $hook
echo "Then open the injection PR in oreilly-claude-review-target and read the Actions log."
