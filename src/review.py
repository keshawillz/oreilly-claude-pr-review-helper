"""Week 1 reviewer: send a diff to Claude and get trustworthy findings back.

    python src/review.py demos/diffs/day04.diff
"""
import json
import sys

import anthropic

from helpers import ROOT, first_text, parse_diff

MODEL = "claude-sonnet-5"
CONFIDENCE_FLOOR = 0.7

client = anthropic.Anthropic()   # reads ANTHROPIC_API_KEY
schema = json.load(open(ROOT / "schemas" / "findings.json"))
rubric = open(ROOT / "prompts" / "review_system.md").read()


def review_diff(diff_text, feedback=None):
    prompt = "Review this diff:\n\n" + diff_text
    if feedback:
        prompt += "\n\nYour last answer had these problems. Fix them:\n"
        for problem in feedback:
            prompt += "- " + problem + "\n"
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=rubric,
        messages=[{"role": "user", "content": prompt}],
        output_config={"format": {"type": "json_schema", "schema": schema}},
    )
    if response.stop_reason in ("refusal", "max_tokens"):
        raise RuntimeError("Incomplete reply, stop_reason=" + response.stop_reason)
    return json.loads(first_text(response))["findings"]


def validate(findings, visible):
    # visible maps each file in the diff to the line numbers the diff shows
    problems = []
    for f in findings:
        name, line = f["file"], f["line"]
        if name not in visible:
            problems.append(f"{name} is not in this diff")
        elif line not in visible[name]:
            problems.append(f"{name} line {line} is not in this diff")
    return problems


def keep_trustworthy(findings, visible):
    keep = []
    for f in findings:
        in_diff = f["file"] in visible and f["line"] in visible[f["file"]]
        sure_enough = f["confidence"] >= CONFIDENCE_FLOOR
        if in_diff and (sure_enough or f["severity"] == "critical"):
            keep.append(f)
    return keep


def review_with_retry(diff_text):
    visible = parse_diff(diff_text)
    findings = review_diff(diff_text)
    problems = validate(findings, visible)
    if problems:                     # retry once, and say what was wrong
        print("retrying once:", problems, file=sys.stderr)
        findings = review_diff(diff_text, feedback=problems)
    return keep_trustworthy(findings, visible)


if __name__ == "__main__":
    for f in review_with_retry(open(sys.argv[1]).read()):
        print(f"[{f['severity']}] {f['file']}:{f['line']} ({f['confidence']:.2f})")
        print("   ", f["issue"])
        print("    fix:", f["suggestion"])
