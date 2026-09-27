"""Grade one trial end to end from files this bundle ships.

  outcome        tests/run_tests.py     target + preserve, reads tests/config.json
  deterministic  tests/test_output.py   hard gates + recorded site/requirement checks
  rubric         tests/rubrics.json     scored by an LLM, needs network

  process    = mean(available process channels)
  score_eval = gate * ((1 - 2*alpha) * outcome + 2*alpha * process)    alpha = 0.05

Writes reward.json (composed), grading.json (every channel and its basis),
final_score.md, or invalid.json when a hard gate voids the run.

Deterministic rule: soft checks only, abstentions excluded. A test named
*_is_recorded_not_scored abstains by construction -- the outcome channel already
pays for those facts through its fail-to-pass targets, so scoring them here would
pay twice. A hard-gate assertion failure voids the trial rather than scoring it.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ALPHA = 0.05
TIMEOUT = int(os.environ.get("LEVI_CHANNEL_TIMEOUT", "3600"))


def _run(cmd: list[str], cwd: str | None = None, env_extra: dict | None = None) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT,
                           env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **(env_extra or {})})
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, f"timeout after {TIMEOUT}s"
    except OSError as exc:
        return 127, str(exc)


def _read(path: Path, default=None):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return default


def outcome_channel(tests_dir: Path, out_dir: Path) -> tuple[float, dict]:
    runner = tests_dir / "run_tests.py"
    if not runner.is_file():
        return 0.0, {"state": "absent", "detail": "tests/run_tests.py missing"}
    code, log = _run([sys.executable, str(runner),
                      "--config", str(tests_dir / "config.json"), "--logs", str(out_dir)])
    doc = _read(out_dir / "reward.json")
    if doc is None:
        return 0.0, {"state": "no-reward-written", "exit": code}
    reason = _read(out_dir / "reward_reason.json", {}) or {}
    return float(doc.get("reward", 0.0)), {
        "state": "scored", "exit": code, "reason": reason.get("reason"),
        "f2p": f"{reason.get('f2p_resolved')}/{reason.get('f2p_total')}",
        "preserve": f"{reason.get('preserve_matched')}/{reason.get('preserve_total')}",
        "source": "tests/run_tests.py",
    }


def _task_uuid(tests_dir: Path) -> str:
    # test_output.py infers the uuid from its own path, which is <uuid>/tests in the
    # bundle but a flat /tests inside the verifier. Supply it explicitly or its
    # uuid hard gate fails and voids every run.
    for parent in (tests_dir.resolve().parent, *tests_dir.resolve().parents):
        if re.fullmatch(r"[0-9a-f-]{36}", parent.name):
            return parent.name
    cfg = _read(tests_dir / "config.json", {}) or {}
    return str(cfg.get("uuid_v5") or cfg.get("task_uuid") or "")


def deterministic_channel(tests_dir: Path, out_dir: Path) -> tuple[float | None, dict]:
    module = tests_dir / "test_output.py"
    if not module.is_file():
        return None, {"state": "absent"}
    junit = out_dir / "deterministic-junit.xml"
    code, log = _run([sys.executable, "-m", "pytest", str(module), "-rA", "--tb=short",
                      "-p", "no:cacheprovider", "-o", "addopts=", f"--junitxml={junit}"], cwd="/",
                     env_extra={"TRINITY_TASK_UUID": _task_uuid(tests_dir)})
    if not junit.is_file():
        return None, {"state": "no-report", "exit": code,
                      "detail": "pytest wrote no junit xml; is pytest installed in the image?"}

    hard_failures: list[str] = []
    scored: list[tuple[str, bool]] = []
    abstained: list[str] = []
    for case in ET.parse(junit).getroot().iter("testcase"):
        name = case.get("name") or ""
        cls = (case.get("classname") or "").split(".")[-1]
        ident = f"{cls}::{name}" if cls else name
        failed = case.find("failure") is not None or case.find("error") is not None
        skipped = case.find("skipped") is not None
        sites = {p.get("name"): p.get("value") for p in case.iter("property")
                 if (p.get("name") or "").startswith(("E1-touched:", "E2-req:"))}

        if name.endswith("_is_recorded_not_scored"):
            abstained.extend(sites or [ident])
        elif not sites:
            if failed:
                hard_failures.append(ident)
        elif skipped:
            abstained.extend(sites)
        else:
            scored.extend((k, v == "reached") for k, v in sites.items())

    if hard_failures:
        return None, {"state": "voided", "hard_failures": hard_failures}
    if not scored:
        return None, {"state": "nothing-scored", "abstained": len(abstained)}

    reached = sum(1 for _, ok in scored if ok)
    return round(reached / len(scored), 4), {
        "state": "scored", "reached": reached, "scored": len(scored),
        "abstained": len(abstained), "hard_failures": [],
        "rule": "reached / scored; soft checks only, abstentions excluded",
        "source": "tests/test_output.py via pytest junit",
    }


def rubric_channel(tests_dir: Path, out_dir: Path) -> tuple[float | None, dict]:
    try:
        from . import judge
    except ImportError as exc:
        return None, {"state": "judge-unavailable", "detail": str(exc)}
    try:
        return judge.score(tests_dir, out_dir)
    except Exception as exc:
        return None, {"state": "judge-error", "detail": f"{type(exc).__name__}: {exc}"}


def run(tests_dir: Path, patch: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    alpha = float(os.environ.get("SCORE_ALPHA", ALPHA))

    outcome, o_det = outcome_channel(tests_dir, out_dir)
    det, d_det = deterministic_channel(tests_dir, out_dir)
    rubric, r_det = rubric_channel(tests_dir, out_dir)

    if d_det.get("state") == "voided":
        doc = {"schema_version": "levi-invalid/1", "reason": "hard_gate_failed",
               "stage": "deterministic", "detail": d_det["hard_failures"]}
        (out_dir / "invalid.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        for stale in ("reward.json", "reward.txt"):
            (out_dir / stale).unlink(missing_ok=True)
        return doc

    present = [c for c in (det, rubric) if c is not None]
    process = round(sum(present) / len(present), 4) if present else None
    gate = 1
    score_eval = (round(gate * ((1 - 2 * alpha) * outcome + 2 * alpha * process), 4)
                  if process is not None else round(outcome, 4))

    grading = {
        "schema_version": "levi-grading/1",
        "outcome": {"score": round(outcome, 4), **o_det},
        "deterministic": {"score": det, **d_det},
        "rubric": {"score": rubric, **r_det},
        "process": {"score": process, "formula": "mean(deterministic, rubric)",
                    "channels_present": len(present)},
        "composition": {
            "alpha": alpha, "gate": gate, "score_eval": score_eval,
            "formula": "gate * ((1 - 2*alpha) * outcome + 2*alpha * process)",
            "fallback": None if process is not None else "outcome only: no process channel",
        },
        "reward": score_eval, "reward_formula": "score_eval",
    }
    (out_dir / "grading.json").write_text(
        json.dumps(grading, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "reward.json").write_text(
        json.dumps({"reward": score_eval, "outcome": round(outcome, 4), "deterministic": det,
                    "rubric": rubric, "process": process}, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "reward.txt").write_text("%.6f\n" % score_eval, encoding="utf-8")

    f = lambda v: "n/a" if v is None else str(v)
    (out_dir / "final_score.md").write_text("\n".join([
        "# Score", "", "| channel | score |", "|---|--:|",
        f"| outcome | {f(round(outcome, 4))} |",
        f"| deterministic | {f(det)} |",
        f"| rubric | {f(rubric)} |",
        f"| **process** = mean(det, rubric) | {f(process)} |", "",
        "| composed | value |", "|---|--:|",
        f"| **score_eval** = gate*((1-2a)*outcome + 2a*process), a={alpha} | {f(score_eval)} |", "",
    ]), encoding="utf-8")
    return grading
