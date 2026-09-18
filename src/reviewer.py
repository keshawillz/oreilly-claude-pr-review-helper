"""Week 2 reviewer: tools, a turn cap, and a cached prefix.

    python src/reviewer.py demos/diffs/day06.diff --repo sample_app
"""
import json
import sys
from pathlib import Path

import tools
from helpers import first_text, parse_diff
from review import MODEL, client, keep_trustworthy, rubric, schema, validate

MAX_TURNS = 8
FINDINGS_FORMAT = {"format": {"type": "json_schema", "schema": schema}}


def build_repo_context(repo_dir):
    """The repo's Python files. They stay the same between PRs, so this is the cached part.

    Sonnet 5 only caches a prefix of 1,024 tokens or more. A bare file list is too short.
    """
    parts = ["Repository files, for reference:"]
    for path in sorted(Path(repo_dir).rglob("*.py")):
        name = str(path.relative_to(repo_dir))
        if name.startswith("."):                   # skip .claude, .venv, and friends
            continue
        parts.append(f"\n===== {name} =====\n{path.read_text()}")
    return "\n".join(parts)


def ask_claude(messages, repo_context):
    return client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=[
            {"type": "text", "text": rubric},
            {"type": "text", "text": repo_context,
             # breakpoint: everything up to here is the cached prefix
             "cache_control": {"type": "ephemeral"}},
        ],
        tools=tools.TOOLS,
        messages=messages,
        output_config=FINDINGS_FORMAT,
    )


def run_tool(block):
    result = {"type": "tool_result", "tool_use_id": block.id}
    try:
        handler = tools.HANDLERS[block.name]       # look up by tool name
        output = handler(**block.input)            # pass arguments by name
        result["content"] = str(output)
    except Exception as error:                     # tell Claude, so it can adjust
        result["content"] = f"Error: {error}"
        result["is_error"] = True
    return result


def add_turn(messages, response, results):
    messages.append({"role": "assistant", "content": response.content})
    messages.append({"role": "user", "content": results})
    return messages


def review_with_tools(diff_text, repo_dir="sample_app"):
    tools.CONTEXT["repo_dir"] = repo_dir
    tools.CONTEXT["diff_text"] = diff_text
    repo_context = build_repo_context(repo_dir)
    messages = [{"role": "user", "content": "Review this diff:\n\n" + diff_text}]

    finished = False
    cache_write = cache_read = uncached = 0   # added up over every call in this review
    for turn in range(MAX_TURNS):      # the Day 6 loop, now with a cap
        response = ask_claude(messages, repo_context)
        cache_write += response.usage.cache_creation_input_tokens
        cache_read += response.usage.cache_read_input_tokens
        uncached += response.usage.input_tokens
        if response.stop_reason != "tool_use":
            finished = True
            break
        results = []
        for block in response.content:
            if block.type == "tool_use":
                results.append(run_tool(block))
        messages = add_turn(messages, response, results)
    if not finished:
        raise RuntimeError(f"No answer after {MAX_TURNS} turns")

    print("  calls:", turn + 1, "| cache write:", cache_write,
          "| cache read:", cache_read, "| uncached:", uncached, file=sys.stderr)

    findings = json.loads(first_text(response))["findings"]
    visible = parse_diff(diff_text)
    for problem in validate(findings, visible):
        print("  dropped:", problem, file=sys.stderr)
    return keep_trustworthy(findings, visible)


if __name__ == "__main__":
    repo = sys.argv[sys.argv.index("--repo") + 1] if "--repo" in sys.argv else "sample_app"
    for f in review_with_tools(open(sys.argv[1]).read(), repo):
        print(f"[{f['severity']}] {f['file']}:{f['line']}  {f['issue']}")
