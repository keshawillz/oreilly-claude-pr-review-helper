"""Day 10: the Week 2 reviewer on a real pull request.

Step 1, MCP: Claude reads the pull request through GitHub's MCP server.
Step 2, our reviewer: tools, the cached repo, and the Week 1 checks.

    usekey; useghtoken
    export TARGET_REPO=keshawillz/oreilly-claude-review-target
    python demos/day10_real_pr.py 1        # the pull request number
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from helpers import ROOT                   # noqa: E402
from review import MODEL, client           # noqa: E402
from reviewer import review_with_tools     # noqa: E402

GITHUB_MCP = ("https://api.githubcopilot.com"
              "/mcp/x/pull_requests/readonly")   # read tools only, same as Day 8


def result_text(block):
    """The text GitHub's tool sent back. It can be a string or a list of text blocks."""
    if isinstance(block.content, str):
        return block.content
    return "".join(part.text for part in block.content if part.type == "text")


def find_diff(value):
    """Find the diff in GitHub's reply. GitHub wraps it in JSON, so unwrap that first."""
    if isinstance(value, str):
        try:
            return find_diff(json.loads(value))        # JSON: look inside it
        except ValueError:
            start = value.find("diff --git")           # plain text: the diff itself
            return value[start:] if start >= 0 else None
    if isinstance(value, dict):
        value = list(value.values())
    if isinstance(value, list):
        for item in value:
            found = find_diff(item)
            if found:
                return found
    return None


def fetch_diff(repo, number):
    """Step 1: Claude asks GitHub for the diff. We keep GitHub's copy, word for word."""
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=4096,
        betas=["mcp-client-2025-11-20"],
        mcp_servers=[{"type": "url", "name": "github", "url": GITHUB_MCP,
                      "authorization_token": os.environ["GITHUB_TOKEN"]}],
        tools=[{"type": "mcp_toolset", "mcp_server_name": "github"}],
        messages=[{"role": "user", "content":
                   f"Get the diff for pull request {number} in {repo}. "
                   "Don't review it. Reply with the single word: done."}],
    )
    replies = []
    for block in response.content:
        if block.type == "mcp_tool_use":
            print("  mcp:", block.name, file=sys.stderr)
        if block.type == "mcp_tool_result":
            replies.append(result_text(block))
            diff = find_diff(replies[-1])
            if diff and "\n+++ " in diff:             # a real diff, one line per line
                return diff
    raise RuntimeError("GitHub's MCP server sent back no usable diff. Check TARGET_REPO, the PR "
                       "number, and that useghtoken ran in this terminal. GitHub replied: "
                       + " | ".join(r[:300] for r in replies))


if __name__ == "__main__":
    diff = fetch_diff(os.environ["TARGET_REPO"], sys.argv[1])
    for f in review_with_tools(diff, ROOT / "sample_app"):   # Step 2: the Week 2 reviewer
        print(f"[{f['severity']}] {f['file']}:{f['line']}  {f['issue']}")
