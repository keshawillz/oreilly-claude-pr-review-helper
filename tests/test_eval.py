import json

import run_golden


def test_scoring_allows_a_small_line_tolerance():
    expected = [{"file": "app/db.py", "line": 39}]
    near = [{"file": "app/db.py", "line": 40}]
    far = [{"file": "app/db.py", "line": 50}, {"file": "app/auth.py", "line": 39}]
    assert run_golden.score(near, expected) == (1, 0)
    assert run_golden.score(far, expected) == (0, 2)
    assert run_golden.score([], expected) == (0, 0)


def test_golden_cases_point_at_real_lines():
    for case in json.load(open("eval/golden/cases.json")):
        workdir = run_golden.checkout_with_diff(case["diff"])
        for expected in case["expected"]:
            lines = (workdir / expected["file"]).read_text().splitlines()
            assert len(lines) >= expected["line"], case["id"]


def test_week2_beats_week1_on_the_cross_file_case():
    week1 = run_golden.run("week1")
    week2 = run_golden.run("week2")
    assert week1["total"] == week2["total"] == 10
    assert week1["hits"] == 9 and week2["hits"] == 10       # the fake only sees case 07 with tools
    assert week1["false_positives"] == week2["false_positives"] == 0
