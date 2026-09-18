"""Score a reviewer against the golden set: ten diffs, each with one seeded issue.

    python eval/run_golden.py                  # Week 1 and Week 2 reviewers
    python eval/run_golden.py --reviewer cli   # through claude -p, as CI runs it
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "eval"))

LINE_TOLERANCE = 2      # within two lines of the seeded issue is a catch


def week1(diff_text, repo_dir):
    from review import review_with_retry           # Week 1: diff only
    return review_with_retry(diff_text), None


def week2(diff_text, repo_dir):
    from reviewer import review_with_tools         # Week 2: tools + context
    return review_with_tools(diff_text, repo_dir), None


def cli(diff_text, repo_dir):
    from cli_reviewer import review_with_cli       # Week 3: claude -p
    return review_with_cli(diff_text, repo_dir)


REVIEWERS = {"week1": week1, "week2": week2, "cli": cli}


def is_match(finding, expected):
    same_file = finding["file"] == expected["file"]
    close = abs(finding["line"] - expected["line"]) <= LINE_TOLERANCE
    return same_file and close


def score(findings, expected_list):
    hits = 0
    for expected in expected_list:
        for finding in findings:
            if is_match(finding, expected):
                hits += 1                       # caught a seeded issue
                break
    false_pos = 0
    for finding in findings:
        matched = False
        for expected in expected_list:
            if is_match(finding, expected):
                matched = True
        if not matched:
            false_pos += 1                      # flagged something clean
    return hits, false_pos


def checkout_with_diff(diff_path):
    """Copy sample_app to a temp folder and apply the diff, like a PR checkout."""
    workdir = Path(tempfile.mkdtemp(prefix="golden-"))
    shutil.copytree(ROOT / "sample_app", workdir, dirs_exist_ok=True)
    for name in [".claude", "schemas", "prompts"]:      # the CLI reviewer needs the Skill
        if (ROOT / name).exists():
            shutil.copytree(ROOT / name, workdir / name, dirs_exist_ok=True)
    subprocess.run(["git", "apply", "-p1", str(ROOT / diff_path)], cwd=workdir, check=True)
    return workdir


def run(name):
    reviewer = REVIEWERS[name]
    cases = json.load(open(ROOT / "eval" / "golden" / "cases.json"))
    report = {"reviewer": name, "cases": []}
    hits = total = false_pos = 0
    for case in cases:
        workdir = checkout_with_diff(case["diff"])
        diff_text = open(ROOT / case["diff"]).read()
        findings, cost = reviewer(diff_text, workdir)
        h, fp = score(findings, case["expected"])
        hits, total, false_pos = hits + h, total + len(case["expected"]), false_pos + fp
        report["cases"].append({"id": case["id"], "hits": h, "false_positives": fp, "cost_usd": cost})
        shutil.rmtree(workdir)
    report.update({"hits": hits, "total": total, "false_positives": false_pos})
    results_dir = ROOT / "eval" / "results"
    results_dir.mkdir(exist_ok=True)
    (results_dir / f"{name}.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    names = ["week1"]
    if (ROOT / "src" / "reviewer.py").exists():         # from Day 6 on
        names.append("week2")
    if "--reviewer" in sys.argv:
        names = [sys.argv[sys.argv.index("--reviewer") + 1]]
    for name in names:
        r = run(name)
        reported = r["hits"] + r["false_positives"]
        print(f"{name}: caught {r['hits']}/{r['total']}, "
              f"{r['false_positives']} false positives, "
              f"precision {r['hits']}/{reported}")
