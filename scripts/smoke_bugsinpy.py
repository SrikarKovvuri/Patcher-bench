#!/usr/bin/env python3
"""Step 1 smoke test: one BugsInPy task fails, gold patch passes. No agent."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = json.loads((ROOT / "suites" / "smoke.json").read_text())
RUN_DIR = ROOT / ".patchpilot" / "bench_runs" / "smoke_001" / TASK["task_id"]
WORKSPACE = ROOT / "workspaces" / f"smoke_{TASK['task_id']}"


def die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def bip(root: Path, tool: str) -> Path:
    return root / "framework" / "bin" / tool


def run_bip(script: Path, args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    if not shutil.which("bash"):
        die("bash not found (install Git Bash or use WSL/Linux)")
    return subprocess.run(
        ["bash", str(script), *args],
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
    )


def run_tests(bip_root: Path, project_dir: Path) -> tuple[int, str]:
    r = run_bip(bip(bip_root, "bugsinpy-test"), ["-w", str(project_dir)])
    out = (r.stdout or "") + (r.stderr or "")
    return r.returncode, out


def main() -> int:
    bip_root = Path(os.environ.get("BUGSINPY_ROOT", ""))
    if not bip_root.is_dir():
        die("Set BUGSINPY_ROOT to a cloned BugsInPy repo")

    project = TASK["project"]
    bug_id = TASK["bug_id"]
    project_dir = WORKSPACE / project
    patch_file = bip_root / "projects" / project / "bugs" / bug_id / "bug_patch.txt"

    shutil.rmtree(WORKSPACE, ignore_errors=True)
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[1/4] checkout buggy {project} #{bug_id}")
    r = run_bip(
        bip(bip_root, "bugsinpy-checkout"),
        ["-p", project, "-i", bug_id, "-v", "0", "-w", str(WORKSPACE)],
    )
    if r.returncode != 0:
        die(r.stderr or r.stdout or "checkout failed")

    print("[2/4] compile + run tests (expect fail)")
    r = run_bip(bip(bip_root, "bugsinpy-compile"), ["-w", str(project_dir)])
    if r.returncode != 0:
        die(r.stderr or r.stdout or "compile failed")

    before_rc, before_out = run_tests(bip_root, project_dir)
    (RUN_DIR / "before_test.log").write_text(before_out, encoding="utf-8")

    print("[3/4] apply gold patch")
    patch = patch_file.read_text(encoding="utf-8")
    (RUN_DIR / "final.diff").write_text(patch, encoding="utf-8")
    patch_path = project_dir / "_gold.patch"
    patch_path.write_text(patch, encoding="utf-8")
    r = subprocess.run(
        ["git", "apply", str(patch_path)],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        die(r.stderr or r.stdout or "git apply failed")

    print("[4/4] rerun tests (expect pass)")
    after_rc, after_out = run_tests(bip_root, project_dir)
    (RUN_DIR / "after_test.log").write_text(after_out, encoding="utf-8")

    reproduced = before_rc != 0
    validation_passed = after_rc == 0
    metrics = {
        "task_id": TASK["task_id"],
        "status": "fixed" if validation_passed else "failed",
        "reproduced": reproduced,
        "validation_passed": validation_passed,
        "before_exit_code": before_rc,
        "after_exit_code": after_rc,
    }
    (RUN_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(metrics, indent=2))
    print(f"artifacts: {RUN_DIR.relative_to(ROOT)}")
    return 0 if reproduced and validation_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
