"""Point the Anthropic SDK at the fake API before any test imports the reviewers."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "eval"))
sys.path.insert(0, str(ROOT / "tests"))

import fake_claude  # noqa: E402

SERVER, URL = fake_claude.start()
os.environ["ANTHROPIC_BASE_URL"] = URL
os.environ["ANTHROPIC_API_KEY"] = "fake-key"
os.chdir(ROOT)
