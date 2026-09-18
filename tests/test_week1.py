import json

import fake_claude
import helpers
import review


def read(path):
    return open(path).read()


def test_parse_diff_lists_visible_lines():
    visible = helpers.parse_diff(read("eval/golden/07-cross-file-percent.diff"))
    assert list(visible) == ["app/orders.py"]
    assert 16 in visible["app/orders.py"]          # the seeded line
    assert 1 not in visible["app/orders.py"]       # outside the hunk


def test_structured_review_finds_the_seeded_bug():
    findings = review.review_with_retry(read("eval/golden/09-inverted-expiry.diff"))
    assert [(f["file"], f["line"], f["severity"]) for f in findings] == [("app/auth.py", 25, "critical")]
    request = fake_claude.REQUESTS[-1]
    assert request["output_config"]["format"]["type"] == "json_schema"
    assert request["model"] == "claude-sonnet-5"
    assert "state three things" in request["system"]


def test_low_confidence_nit_is_dropped():
    findings = review.review_with_retry(read("demos/diffs/day04.diff"))
    issues = [f["issue"] for f in findings]
    assert any("None" in issue for issue in issues)             # the real bug stays
    assert not any("inlined" in issue for issue in issues)      # the 0.4 nit goes


def test_invented_line_triggers_one_retry(monkeypatch):
    monkeypatch.setenv("FAKE_CLAUDE_BAD_LINE", "1")
    before = len(fake_claude.REQUESTS)
    findings = review.review_with_retry(read("eval/golden/02-pagination-off-by-one.diff"))
    assert len(fake_claude.REQUESTS) - before == 2              # first call + one retry
    assert "is not in this diff" in json.dumps(fake_claude.REQUESTS[-1]["messages"])
    assert all(f["line"] != 9999 for f in findings)


def test_validate_names_the_problem():
    visible = {"app/db.py": {10, 11}}
    problems = review.validate([{"file": "app/db.py", "line": 99}, {"file": "nope.py", "line": 1}], visible)
    assert problems == ["app/db.py line 99 is not in this diff", "nope.py is not in this diff"]
