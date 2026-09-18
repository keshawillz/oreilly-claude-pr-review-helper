# oreilly-claude-pr-review-helper

The companion repo for **Claude Lunch & Learn: Zero to Agent in 20 Days**.

You build one thing across 20 sessions: an AI code reviewer. Day 1 is a single API call against a diff. By Day 20 the same logic runs in GitHub Actions, reviews every pull request, suggests tests, and posts inline comments at the exact file and line.

The rule that holds all month: the agent comments. It never approves and never blocks a merge.

## Get the code

```bash
git clone https://github.com/keshawillz/oreilly-claude-pr-review-helper.git
```

The app that gets reviewed lives in its own repo: https://github.com/keshawillz/oreilly-claude-review-target

## Catch up in two minutes

Every session ends with a git tag, `day-01` through `day-20`. Each tag is the exact code where that day's demo finished.

```bash
git checkout day-07          # any day you missed
cat demos/day07_multi_tool.sh
bash demos/day07_multi_tool.sh
```

`main` holds the latest session.

### Get each new session

```bash
git checkout main
git pull
git checkout day-03
```

Swap `day-03` for the session you want. If you edited files during a session, run `git checkout -- .` first.

## Try it without spending tokens

`tests/fake_claude.py` is a stand-in for the Claude API. It is not a model. It spots the seeded bugs with plain string checks and answers in the same JSON shapes the real API uses, so you can rehearse the Week 1 and Week 2 demos offline.

```bash
python tests/fake_claude.py                       # terminal 1
export ANTHROPIC_BASE_URL=http://127.0.0.1:8765   # terminal 2
export ANTHROPIC_API_KEY=fake-key
bash demos/day06_tool_use.sh
```

Unset both variables to talk to the real API again.

## Run the tests

```bash
pip install -r requirements.txt
python -m pytest tests sample_app/tests
```

The tests start the fake API on their own. They need no key and no network.

## What is where

| Path | What it is | Arrives |
| --- | --- | --- |
| `src/review.py` | Week 1 reviewer: schema, rubric, confidence filter, validate and retry once | Days 1 to 4 |
| `src/tools.py`, `src/reviewer.py` | Week 2 reviewer: tools, a turn cap, a cached prefix | Days 6 to 9 |
| `src/helpers.py` | `first_text`, `parse_diff`, `read_repo_file` | Days 2, 4, 6 |
| `schemas/findings.json` | The output contract, shared by the API and `--json-schema` | Day 2 |
| `prompts/` | The review rubric and the reviewer identity file | Days 3, 16 |
| `demos/day08_mcp.py` | A real PR read through GitHub's remote MCP server | Day 8 |
| `.claude/commands/review-diff.md` | The `/review-diff` command | Day 12 |
| `.claude/skills/pr-review/` | The Skill: procedure, rubric, test suggestions, incremental review | Days 13, 14, 19 |
| `.claude/CLAUDE.md` | Project facts for CI runs: testing standards, fixtures, severity | Day 13 |
| `.github/workflows/review.yml` | The Claude Code GitHub Action workflow | Days 17, 19 |
| `.claude/hooks/deny_approve.py` | PreToolUse hook that denies approve and merge | Day 18 |
| `eval/` | Golden set, scoring harness, CLI wrapper, cost report, batch job | Payoff days: 5, 10, 15, 20 |
| `sample_app/` | The small shop backend that gets reviewed | Day 1 |
| `demos/` | One script per session, plus the demo diffs | Daily |

## The golden set

`eval/golden/` holds ten diffs against `sample_app`. Each one plants a single known bug, and `cases.json` records its file and line. A finding within two lines of the seeded issue counts as a catch.

```bash
python eval/run_golden.py                  # Week 1 and Week 2 reviewers
python eval/run_golden.py --reviewer cli   # through claude -p, as CI runs it
python eval/golden/make_cases.py           # rebuild the diffs after you add a variant
```

## Schedule

| Week | Days | Theme |
| --- | --- | --- |
| 1 | 1 to 5 | The reviewer's brain: prompting and structured output |
| 2 | 6 to 10 | Give it tools and context: tool use, MCP, prompt caching |
| 3 | 11 to 15 | Teach it your standards: Claude Code headless, a Skill, CLAUDE.md |
| 4 | 16 to 20 | Ship it: review isolation, GitHub Actions, hooks, evaluation and cost |

## Day-by-day changelog

| Tag | What changed |
| --- | --- |
| day-01 | `src/review.py`: one Messages API call that reviews a diff |
| day-02 | `schemas/findings.json`, `output_config.format`, findings as JSON |
| day-03 | `prompts/review_system.md`: the rubric becomes the system prompt |
| day-04 | Confidence field, `parse_diff`, validate and retry once, threshold filter |
| day-05 | Golden set, `eval/run_golden.py`, offline tests |
| day-06 | `get_file` tool, the tool loop, `read_repo_file` path guard |
| day-07 | `list_changed_files`, `run_linter`, dispatch table, `MAX_TURNS` |
| day-08 | `demos/day08_mcp.py`: GitHub MCP server, read-only toolset |
| day-09 | Cached prefix: rubric plus repo context, explicit breakpoint |
| day-10 | Week 1 and Week 2 reviewers scored side by side |
| day-11 | `demos/day11.sh`: interactive, the hang, `-p`, `--bare`, `--model` |
| day-12 | `/review-diff` command, JSON envelope, `--json-schema`, jq |
| day-13 | `pr-review` Skill and the CI section of `.claude/CLAUDE.md` |
| day-14 | Test suggestions in the Skill, `suggested_tests` in the schema |
| day-15 | `eval/cli_reviewer.py`: the golden set through `claude -p` |
| day-16 | `prompts/reviewer.md`, two invocations with no shared session |
| day-17 | `.github/workflows/review.yml`, fenced tools, fail open |
| day-18 | `deny_approve.py` hook, registered in `.claude/settings.json` |
| day-19 | Incremental review: findings carried between runs |
| day-20 | `eval/cost_report.py`, `eval/nightly_batch.py`, full test suite |
