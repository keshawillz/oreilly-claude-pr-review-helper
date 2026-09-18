#!/usr/bin/env bash
# Day 15: golden-set run three, through the CLI. This is how CI will run it.
set -e
python eval/run_golden.py --reviewer cli
