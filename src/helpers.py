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
