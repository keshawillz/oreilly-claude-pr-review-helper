"""Small helpers shared by the reviewers. Each section names the day it arrives."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent   # the repo root


# ---- Day 02: read Claude's reply ----
def first_text(response):
    """Return the text of the first text block in a Messages API response."""
    for block in response.content:
        if block.type == "text":
            return block.text
    return ""


# ---- Day 04: know which lines a diff touches ----
def parse_diff(diff_text):
    """Map each file in a unified diff to the new-file line numbers it shows.

    Returns a dictionary like {"app/orders.py": {12, 13, 14, 15}}.
    Added lines and context lines both count, because both are visible in the diff.
    """
    visible = {}
    current_file = None
    new_line = 0
    for line in diff_text.splitlines():
        if line.startswith("+++ "):
            current_file = line[4:].strip()
            if current_file.startswith("b/"):
                current_file = current_file[2:]
            visible[current_file] = set()
        elif line.startswith("@@"):
            match = re.search(r"\+(\d+)", line)      # @@ -12,6 +12,8 @@
            new_line = int(match.group(1))
        elif current_file is None or line.startswith("---"):
            continue
        elif line.startswith("+") or line.startswith(" "):
            visible[current_file].add(new_line)
            new_line += 1
        # lines that start with "-" exist only in the old file, so skip them
    return visible


# ---- Day 06: read files safely ----
def read_repo_file(repo_dir, path):
    """Read a file for Claude, but only if it sits inside repo_dir.

    A path that comes from the model is untrusted input.
    """
    repo_dir = Path(repo_dir).resolve()
    target = (repo_dir / path).resolve()
    if repo_dir != target and repo_dir not in target.parents:
        raise ValueError(f"{path} is outside the repository")
    if not target.is_file():
        raise ValueError(f"{path} does not exist")
    return target.read_text()
