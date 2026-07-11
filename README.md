# Patcher Bench

Benchmark runner + debugging harness for evaluating coding agents on real Python bugs.

## Status

Work in progress. Step 1 smoke test is in `scripts/smoke_bugsinpy.py`.

## Step 1 smoke test

Proves one BugsInPy task fails on the buggy version and passes after the gold patch.

```bash
git clone https://github.com/soarsmu/BugsInPy
export BUGSINPY_ROOT=/path/to/BugsInPy   # Git Bash / WSL / Linux
python scripts/smoke_bugsinpy.py
```

Writes artifacts to `.patchpilot/bench_runs/smoke_001/black_3/`:
`before_test.log`, `after_test.log`, `final.diff`, `metrics.json`.
