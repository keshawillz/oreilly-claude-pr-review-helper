# Setup

You do not need everything on Day 1. Install what each week needs.

## Before Day 1
- Python 3.10 or newer
- `pip install -r requirements.txt`
- An Anthropic API key with a small spending cap. Create it in the Claude Console, then:
  ```bash
  export ANTHROPIC_API_KEY="sk-ant-..."
  ```
- git, to check out the daily tags

Check it works:
```bash
python src/review.py demos/diffs/day01.diff
```

No key yet? See "Try it without spending tokens" in the README.

## Before Week 2 (Day 8)
- A GitHub account
- Your own copy of `oreilly-claude-review-target`. Fork https://github.com/keshawillz/oreilly-claude-review-target and untick "Copy the main branch only" so the pull request branches come with it.
- A personal access token with read access to your copy of `oreilly-claude-review-target`
  ```bash
  export GITHUB_TOKEN="ghp_..."
  export TARGET_REPO="your-username/oreilly-claude-review-target"
  ```

## Before Week 3 (Day 11)
- Claude Code. The native installer needs no Node.js:
  ```bash
  curl -fsSL https://claude.ai/install.sh | bash
  ```
- `jq` on your path (Day 12), for reading fields out of the JSON envelope
  - macOS: `brew install jq`
  - Ubuntu or Debian: `sudo apt-get install jq`

## Before Week 4 (Day 17)
- Your own copy of `oreilly-claude-review-target`, so you can run the workflow yourself
- The Claude GitHub App installed on that repo, and an `ANTHROPIC_API_KEY` repository secret. Running `/install-github-app` inside Claude Code does both.
- Open demo pull requests from a branch in the same repo. On public repos GitHub withholds secrets from fork PRs, so the review would never run.

## Cannot install locally?
Open this repo in GitHub Codespaces. The included devcontainer installs Python, the requirements, jq, the GitHub CLI, and Claude Code.
