"""Day 6: one tool, and the loop that serves it.

    python src/reviewer.py demos/diffs/day06.diff --repo sample_app
"""
import json
import sys

import tools
from helpers import first_text
from review import client, rubric, schema

FINDINGS_FORMAT = {"format": {"type": "json_schema", "schema": schema}}


def review_with_tools(diff_text, repo_dir="sample_app"):
    tools.CONTEXT["repo_dir"] = repo_dir
    tools.CONTEXT["diff_text"] = diff_text
    messages = [{"role": "user", "content": "Review this diff:\n\n" + diff_text}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-5", max_tokens=4096, system=rubric,
            tools=tools.TOOLS, messages=messages, output_config=FINDINGS_FORMAT)
        if response.stop_reason != "tool_use":
            break                                  # Claude is finished
        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in response.content:
            if block.type == "tool_use":
                text = tools.get_file(block.input["path"])   # stays in the repo
                results.append({"type": "tool_result",
                                "tool_use_id": block.id, "content": text})
        messages.append({"role": "user", "content": results})

    return json.loads(first_text(response))["findings"]


if __name__ == "__main__":
    repo = sys.argv[sys.argv.index("--repo") + 1] if "--repo" in sys.argv else "sample_app"
    for f in review_with_tools(open(sys.argv[1]).read(), repo):
        print(f"[{f['severity']}] {f['file']}:{f['line']}  {f['issue']}")
