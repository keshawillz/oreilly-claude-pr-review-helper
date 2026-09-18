#!/usr/bin/env python3
"""PreToolUse hook: this agent comments. It never approves or merges.

Claude Code sends the pending tool call as JSON on stdin. Printing a deny
decision stops the call before it runs, whatever the model decided.
"""
import json
import sys

BLOCKED_TEXT = ["gh pr merge", "--approve", '"approve"']
COMMENT_FIELDS = ["body", "comment"]  # what the reviewer writes. It may quote the attack.

event = json.load(sys.stdin)        # Claude Code sends the pending call
tool_name = event["tool_name"].lower()
checked = {k: v for k, v in event["tool_input"].items() if k not in COMMENT_FIELDS}
tool_input = json.dumps(checked).lower()

blocked = "merge" in tool_name
for text in BLOCKED_TEXT:
    if text in tool_input:
        blocked = True

if blocked:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason":
            "This agent comments only. It never approves or merges.",
    }}))
sys.exit(0)                         # exit 0 so the JSON decision is read
