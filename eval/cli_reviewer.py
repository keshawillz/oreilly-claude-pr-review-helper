"""Run the pr-review Skill through the Claude Code CLI, the same way CI does.

    python eval/cli_reviewer.py eval/golden/09-inverted-expiry.diff
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = open(ROOT / "schemas" / "findings.json").read()


def review_with_cli(diff_text, repo_dir="."):
    result = subprocess.run(
        ["claude", "-p", "/pr-review",
         "--output-format", "json",
         "--json-schema", SCHEMA,
         "--model", "claude-sonnet-5",
         "--max-turns", "8",
         "--no-session-persistence"],
        input=diff_text,                   # the diff arrives on stdin
        cwd=repo_dir,                      # where .claude/ and the code live
        capture_output=True, text=True)
    try:
        envelope = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError("claude did not return JSON: " + result.stderr)
    if result.returncode != 0 or envelope.get("is_error"):
        raise RuntimeError("claude failed: " + str(envelope.get("result")))
    findings = envelope["structured_output"]["findings"]
    return findings, envelope["total_cost_usd"]


if __name__ == "__main__":
    import shutil
    import sys
    from run_golden import checkout_with_diff       # the same PR-style checkout the golden set uses
    workdir = checkout_with_diff(sys.argv[1])       # sample_app + .claude, with the diff applied
    try:
        findings, cost = review_with_cli(open(ROOT / sys.argv[1]).read(), workdir)
    finally:
        shutil.rmtree(workdir)
    print(json.dumps(findings, indent=2))
    print(f"cost: ${cost:.4f}")
