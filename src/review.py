import json
import sys

import anthropic

from helpers import ROOT, first_text

client = anthropic.Anthropic()
schema = json.load(open(ROOT / "schemas" / "findings.json"))
rubric = open(ROOT / "prompts" / "review_system.md").read()


def review_diff(diff_text):
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=4096,
        system=rubric,
        messages=[{"role": "user",
                   "content": "Review this diff:\n\n" + diff_text}],
        output_config={"format": {"type": "json_schema",
                                  "schema": schema}},
    )
    return json.loads(first_text(response))["findings"]


if __name__ == "__main__":
    for f in review_diff(open(sys.argv[1]).read()):
        print(f"[{f['severity']}] {f['file']}:{f['line']}")
        print("   ", f["issue"])
        print("    fix:", f["suggestion"])
