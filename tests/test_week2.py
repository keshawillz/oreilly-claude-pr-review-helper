import pytest

import fake_claude
import helpers
import reviewer
import tools


def read(path):
    return open(path).read()


def test_read_repo_file_refuses_to_leave_the_repo():
    assert "TAX_RATE" in helpers.read_repo_file("sample_app", "app/pricing.py")
    with pytest.raises(ValueError):
        helpers.read_repo_file("sample_app", "../src/review.py")
    with pytest.raises(ValueError):
        helpers.read_repo_file("sample_app", "/etc/passwd")


def test_tool_loop_fetches_the_file_and_finds_the_cross_file_bug():
    import review
    diff = read("eval/golden/07-cross-file-percent.diff")
    assert review.review_with_retry(diff) == []                  # Week 1 misses it
    findings = reviewer.review_with_tools(diff, "sample_app")    # Week 2 catches it
    assert [(f["file"], f["line"]) for f in findings] == [("app/orders.py", 16)]
    last = fake_claude.REQUESTS[-1]
    assert last["messages"][1]["content"][0]["type"] == "tool_use"
    assert "fraction between 0 and 1" in last["messages"][2]["content"][0]["content"]


def test_cache_breakpoint_sits_on_the_static_block_only():
    reviewer.review_with_tools(read("eval/golden/01-sql-injection.diff"), "sample_app")
    system = fake_claude.REQUESTS[-1]["system"]
    assert "cache_control" not in system[0]
    assert system[1]["cache_control"] == {"type": "ephemeral"}
    assert "cache_control" not in str(fake_claude.REQUESTS[-1]["messages"])


def test_tools_list_and_lint():
    tools.CONTEXT["repo_dir"] = "sample_app"
    tools.CONTEXT["diff_text"] = read("demos/diffs/day07.diff")
    assert tools.list_changed_files() == ["app/db.py", "app/orders.py"]
    assert "No lint problems" in tools.run_linter("app/pricing.py")
    with pytest.raises(ValueError):
        tools.run_linter("../src/review.py")


def test_a_failing_tool_reports_is_error():
    class Block:
        id, name, input = "toolu_1", "get_file", {"path": "missing.py"}
    result = reviewer.run_tool(Block())
    assert result["is_error"] is True and "does not exist" in result["content"]
