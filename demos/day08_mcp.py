"""Day 8: review a real pull request through GitHub's remote MCP server.

    export GITHUB_TOKEN=...            # read access to the target repo is enough
    export TARGET_REPO=your-username/oreilly-claude-review-target
    python demos/day08_mcp.py 1        # the pull request number
"""
import os
import sys

import anthropic

client = anthropic.Anthropic()
GITHUB_MCP = ("https://api.githubcopilot.com"
              "/mcp/x/pull_requests/readonly")   # read tools only


def review_pull_request(repo, number):
    response = client.beta.messages.create(
        model="claude-sonnet-5",
        max_tokens=4096,
        betas=["mcp-client-2025-11-20"],
        mcp_servers=[{"type": "url", "name": "github", "url": GITHUB_MCP,
                      "authorization_token": os.environ["GITHUB_TOKEN"]}],
        tools=[{"type": "mcp_toolset", "mcp_server_name": "github"}],
        messages=[{"role": "user", "content":
                   f"Review pull request {number} in {repo}. "
                   "Read the diff before you comment."}],
    )
    for block in response.content:
        if block.type == "text":
            print(block.text)
        else:
            print(f"[{block.type}]")           # the MCP tool calls and results
    return response


if __name__ == "__main__":
    review_pull_request(os.environ["TARGET_REPO"], sys.argv[1])
