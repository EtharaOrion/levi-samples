"""Shared live submission runner for image-dependent instruments.

Phase 1 items 8f, 8i, 8e, and 8o each name executions that only the pinned
sanitized image can produce: the empty-submission replay of G-CON-EMPTY, the
unmodified-base grading of G-VER-BASELINE, the rebuild-and-grade of
G-CAL-REPRODUCIBILITY, and the no-op and oracle re-runs of rewarddefinition.
This module executes those runs through the stock Harbor path the delivery
block binds: the committed tests/Dockerfile builds the verifier image from
the pinned digest, and tests/test.sh drives run_tests.py which writes the
bound reward contract files. Results are cached by content digest so the
expensive container runs execute once per distinct workspace state, and every
consumer reads the same measured bytes rather than re-deriving its own.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import core
from adversary import (
    APPLY_FAILURE_EXIT,
    LIVE_CACHE_RELATIVE,
    LIVE_TIMEOUT_SECONDS,
    _ensure_verifier_image,
)

STATUS_MEASURED = "measured"
STATUS_BUILD_FAILED = "build-failed"
STATUS_APPLY_FAILED = "apply-failed"
STATUS_INCOMPLETE = "incomplete"
STATUS_UNPARSEABLE = "unparseable"
STATUS_IMAGE_ABSENT = "image-absent"


def _config(bundle: Path) -> dict[str, Any]:
    """Load the committed verifier config; the repo_dir key names the workspace."""
    try:
        return json.loads((bundle / "tests" / "config.json").read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _cache_path(base: Path, bundle: Path, label: str, digest: str) -> Path:
    return (
        base
        / core.AUDIT_DIRNAME
        / LIVE_CACHE_RELATIVE
        / bundle.name
        / (f"exec-{label}-{digest[:12]}.json")
    )


def _runtime_present(bundle: Path) -> bool:
    """True when the pinned sanitized image resolves in the local daemon."""
    try:
        import tomllib

        manifest = tomllib.loads((bundle / "task.toml").read_text())
    except Exception:
        return False
    reference = str(((manifest.get("environment") or {}).get("docker_image")) or "")
    if not reference:
        return False
    probe = core.run_capture(
        ["docker", "image", "inspect", reference],
        artifact_id=f"liveexec-inspect-{bundle.name[:8]}",
        timeout=60.0,
    )
    return probe.exit_code == 0


def run_submission(
    base: Path,
    bundle: Path,
    label: str,
    diff_text: str = "",
    apply_gold: bool = False,
) -> dict[str, Any]:
    """Execute one submission through the stock Harbor path and read the reward.

    The workspace starts at the image's committed base; apply_gold applies the
    committed oracle fix.patch first, and diff_text applies on top of that.
    The bound reward contract files under /logs/verifier are read back whole so
    consumers can reconcile componentwise rather than trusting a scalar.
    """
    gold = (bundle / "solution" / "fix.patch").read_text() if apply_gold else ""
    digest = core.sha256_bytes((gold + "\n--\n" + diff_text).encode())
    cache = _cache_path(base, bundle, label, digest)
    if cache.exists():
        try:
            cached = json.loads(cache.read_text())
            if cached.get("digest") == digest:
                cached["cache_hit"] = True
                cached["artifacts"] = []
                return cached
        except (OSError, json.JSONDecodeError):
            pass

    result: dict[str, Any] = {
        "label": label,
        "bundle": bundle.name,
        "digest": digest,
        "apply_gold": apply_gold,
        "cache_hit": False,
        "status": STATUS_INCOMPLETE,
        "reward": None,
        "reason": "",
        "components": {},
        "artifacts": [],
    }
    if not _runtime_present(bundle):
        result["status"] = STATUS_IMAGE_ABSENT
        return result

    tag, build_artifacts = _ensure_verifier_image(bundle)
    result["artifacts"] = list(build_artifacts)
    if tag is None:
        result["status"] = STATUS_BUILD_FAILED
        return result

    config = _config(bundle)
    repo_dir = str(config.get("repo_dir") or "")
    if not repo_dir:
        result["status"] = STATUS_INCOMPLETE
        result["reason"] = "config.json carries no repo_dir"
        return result

    with tempfile.TemporaryDirectory() as scratch:
        work = Path(scratch) / "probework"
        logs = Path(scratch) / "logs"
        work.mkdir()
        logs.mkdir()
        steps = [f"cd {repo_dir}"]
        if gold:
            (work / "forward.patch").write_text(gold)
            steps.append(
                "git apply --whitespace=nowarn /probework/forward.patch"
                f" || exit {APPLY_FAILURE_EXIT}"
            )
        if diff_text:
            (work / "probe.diff").write_text(diff_text)
            steps.append(
                f"git apply --whitespace=nowarn /probework/probe.diff || exit {APPLY_FAILURE_EXIT}"
            )
        steps.append("bash /tests/test.sh")
        run = core.run_capture(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                "none",
                "-v",
                f"{work}:/probework:ro",
                "-v",
                f"{logs}:/logs",
                tag,
                "bash",
                "-c",
                "; ".join(steps),
            ],
            artifact_id=f"liveexec-run-{bundle.name[:8]}-{label}",
            timeout=LIVE_TIMEOUT_SECONDS,
        )
        result["artifacts"].append(run)
        if run.blocked_reason or run.timed_out:
            result["status"] = STATUS_INCOMPLETE
            result["reason"] = run.blocked_reason or "timeout"
            return result
        if run.exit_code == APPLY_FAILURE_EXIT:
            result["status"] = STATUS_APPLY_FAILED
            return result
        verifier_dir = logs / "verifier"
        try:
            reward_doc = json.loads((verifier_dir / "reward.json").read_text())
            reward = float(reward_doc["reward"])
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
            result["status"] = STATUS_UNPARSEABLE
            return result
        components: dict[str, Any] = {}
        try:
            components = json.loads((verifier_dir / "reward_reason.json").read_text())
        except (OSError, json.JSONDecodeError):
            components = {}
        result["status"] = STATUS_MEASURED
        result["reward"] = reward
        result["reason"] = str(components.get("reason", ""))
        result["components"] = components

    cache.parent.mkdir(parents=True, exist_ok=True)
    persisted = dict(result)
    persisted["artifacts"] = []
    cache.write_text(json.dumps(persisted, indent=2, sort_keys=True) + "\n")
    return result


def empty_run(base: Path, bundle: Path) -> dict[str, Any]:
    """Empty submission against the unmodified base workspace."""
    return run_submission(base, bundle, "empty")


def oracle_run(base: Path, bundle: Path) -> dict[str, Any]:
    """Committed oracle fix.patch applied, then graded."""
    return run_submission(base, bundle, "oracle", apply_gold=True)


__all__ = [
    "STATUS_APPLY_FAILED",
    "STATUS_BUILD_FAILED",
    "STATUS_IMAGE_ABSENT",
    "STATUS_INCOMPLETE",
    "STATUS_MEASURED",
    "STATUS_UNPARSEABLE",
    "empty_run",
    "oracle_run",
    "run_submission",
]
