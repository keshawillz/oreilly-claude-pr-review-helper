import json
import sys

import anthropic

from helpers import ROOT, first_text

client = anthropic.Anthropic()
# One schema file. Day 12 hands this same file to the CLI.
schema = json.load(open(ROOT / "schemas" / "findings.json"))


def review_diff(diff_text):
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=4096,
        messages=[{"role": "user",
                   "content": "Review this diff:\n\n" + diff_text}],
        output_config={"format": {"type": "json_schema",
                                  "schema": schema}},
    )
    return json.loads(first_text(response))["findings"]


if __name__ == "__main__":
    for f in review_diff(open(sys.argv[1]).read()):
        print(f["severity"], f["file"], f["line"], "-", f["issue"])
