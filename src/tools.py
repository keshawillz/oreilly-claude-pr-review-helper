"""The tools Claude can ask for, and the Python that runs them."""
import subprocess
import sys

from helpers import parse_diff, read_repo_file

# The review in progress. review_with_tools() fills this in before the loop starts.
CONTEXT = {"repo_dir": ".", "diff_text": ""}


# ---- Day 06: one tool ----
def get_file(path):
    print("  tool: get_file", path, file=sys.stderr)
    return read_repo_file(CONTEXT["repo_dir"], path)


TOOLS = [{
    "name": "get_file",
    "description": "Read one full file from the repo. Use it when "
                   "the diff does not show enough to judge a change.",
    "input_schema": {"type": "object", "required": ["path"],
                     "properties": {"path": {"type": "string"}}},
}]

HANDLERS = {"get_file": get_file}     # tool name -> Python function
