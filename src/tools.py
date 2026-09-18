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


# ---- Day 07: a small toolbox ----
def list_changed_files():
    print("  tool: list_changed_files", file=sys.stderr)
    return sorted(parse_diff(CONTEXT["diff_text"]))


def run_linter(path):
    print("  tool: run_linter", path, file=sys.stderr)
    read_repo_file(CONTEXT["repo_dir"], path)      # same path guard as get_file
    result = subprocess.run([sys.executable, "-m", "pyflakes", path],
                            cwd=CONTEXT["repo_dir"], capture_output=True, text=True)
    return result.stdout + result.stderr or "No lint problems found."


TOOLS += [{
    "name": "list_changed_files",
    "description": "List every file this diff changes. Call it first to get oriented.",
    "input_schema": {"type": "object", "properties": {}},
}, {
    "name": "run_linter",
    "description": "Run the linter on one file. Use it before you report "
                   "unused names or undefined variables.",
    "input_schema": {"type": "object", "required": ["path"],
                     "properties": {"path": {"type": "string"}}},
}]

HANDLERS = {                       # tool name -> Python function
    "get_file": get_file,
    "list_changed_files": list_changed_files,
    "run_linter": run_linter,
}
