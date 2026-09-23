"""Phase 1 item 3 reconnaissance: the recorded facts every instrument reasons from.

The contract requires this module to record the git SHA, the dirty state, runtime
versions, roots, manifests, scanner database versions and digests, and the surface
map. Those facts are captured once and written into evidence.yaml rather than
re-derived per instrument, because a disposition that depends on when a fact was
read is not reproducible.

The dirty bit is recorded as a boolean. A dirty tree presented as clean is a BLOCK
under the disposition vocabulary, so this module never softens the bit into prose
and records the entry list separately as detail.
"""

from __future__ import annotations

import datetime
import platform
import shutil
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from core import (
    AUDIT_DIRNAME,
    CAPABILITIES_FILENAME,
    SCOPE_APPROVED_FILENAME,
    SCOPE_FILENAME,
    bundle_roots,
    lane_of,
    project_root,
    run_capture,
    sha256_path,
)

SCANNER_BINARIES = (
    "semgrep",
    "trufflehog",
    "osv-scanner",
    "syft",
    "grype",
    "hadolint",
    "trivy",
    "gitleaks",
    "bandit",
    "pip-audit",
    "ruff",
    "docker",
    "git",
    "jq",
    "uv",
)

SCANNER_DATABASE_NAMES = (
    "semgrep",
    "osv-scanner",
    "grype",
    "trivy",
    "gitleaks",
    "hadolint",
)


@dataclass
class Recon:
    """The recorded state of the tree and host at the instant the run began."""

    root: Path
    git_sha: str
    branch: str
    dirty_bit: bool
    dirty_entries: list[str]
    history_depth: int
    runtime: dict
    binaries: dict
    scanner_databases: dict
    bundles: list[dict]
    scope: dict
    captured_at: str = field(default_factory=lambda: _utc_now())

    def to_row(self) -> dict:
        return {
            "root": str(self.root),
            "captured_at": self.captured_at,
            "git_sha": self.git_sha,
            "branch": self.branch,
            "dirty_bit": self.dirty_bit,
            "dirty_entries": self.dirty_entries,
            "history_depth": self.history_depth,
            "runtime": self.runtime,
            "binaries": self.binaries,
            "scanner_databases": self.scanner_databases,
            "bundles": self.bundles,
            "scope": self.scope,
        }


def _git(root: Path, *args: str) -> tuple[int, str]:
    artifact = run_capture(
        ["git", *args], artifact_id=f"git-{'-'.join(args)}", cwd=root, timeout=60.0
    )
    return artifact.exit_code, artifact.stdout.strip()


def collect_runtime() -> dict:
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "implementation": platform.python_implementation(),
    }


def collect_binaries(names: Sequence[str] = SCANNER_BINARIES) -> dict:
    """Record which declared binaries resolve on this host and where.

    A binary that does not resolve is recorded as absent rather than omitted, so
    the registry's disposition cap on absence has an explicit fact to key on.
    """
    found: dict[str, dict] = {}
    for name in sorted(names):
        path = shutil.which(name)
        entry: dict = {"present": path is not None, "path": path or ""}
        if path:
            entry["version"] = _probe_version(name)
        found[name] = entry
    return found


def _probe_version(name: str) -> str:
    for flag in ("--version", "version", "-V"):
        artifact = run_capture(
            [name, flag], artifact_id=f"version-{name}-{flag.strip('-')}", timeout=30.0
        )
        if artifact.blocked_reason:
            return ""
        if artifact.exit_code == 0:
            text = (artifact.stdout or artifact.stderr).strip()
            return text.splitlines()[0] if text else ""
    return ""


def collect_scanner_databases(root: Path | None = None) -> dict:
    """Record the pinned rule and vulnerability databases each scanner will read.

    Phase 1 item 5 forbids an unpinned database and the disposition vocabulary
    makes an unpinned scanner database a BLOCK, so an unresolved pin is recorded
    as an explicit null with a reason rather than left out of the document.

    The pin state is read out of the config the scanner will actually be invoked
    with, never inferred from the config file merely existing. A file existing
    says nothing about whether the rule or vulnerability data behind it is fixed,
    and treating presence as proof of pinning would let an unpinned feed pass as
    pinned. Each config also declares whether the instrument runs at all, and the
    source paths it pins are digested here so a rule edit is visible in evidence.
    """
    base = root or project_root()
    config_dir = base / AUDIT_DIRNAME / "scanner-configs"
    databases: dict[str, dict] = {}
    for name in SCANNER_DATABASE_NAMES:
        config = config_dir / f"{name}.yaml"
        if not config.exists():
            databases[name] = {
                "config_path": "",
                "config_digest": None,
                "pin_state": "unresolved",
                "runs": False,
                "sources": [],
                "reason": "scanner config not yet authored in .audit",
            }
            continue
        declared = _load_scanner_config(config)
        database = declared.get("database") or {}
        sources = []
        for entry in database.get("sources") or []:
            source = base / str(entry.get("path", ""))
            sources.append(
                {
                    "path": str(entry.get("path", "")),
                    "digest": sha256_path(source) if source.is_file() else None,
                    "present": source.is_file(),
                }
            )
        databases[name] = {
            "config_path": str(config.relative_to(base)),
            "config_digest": sha256_path(config),
            "pin_state": str(database.get("pin_state") or "unresolved"),
            "runs": bool(declared.get("runs", False)),
            "sources": sources,
            "reason": str(declared.get("runs_basis") or database.get("pin_basis") or ""),
        }
    return databases


def _load_scanner_config(path: Path) -> dict:
    """Parse one scanner config, failing closed to an empty declaration."""
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def collect_bundles(root: Path | None = None) -> list[dict]:
    """Enumerate every resident bundle with its lane and top-level surface shape."""
    base = root or project_root()
    rows: list[dict] = []
    for bundle in sorted(bundle_roots(base), key=lambda p: p.name):
        entries = sorted(child.name for child in bundle.iterdir() if not child.name.startswith("."))
        rows.append(
            {
                "uuid": bundle.name,
                "lane": lane_of(bundle, base),
                "path": str(bundle.relative_to(base)),
                "entries": entries,
                "has_tests": (bundle / "tests").is_dir(),
                "has_solution": (bundle / "solution").is_dir(),
                "has_trajectories": (bundle / "trajectories").is_dir(),
                "has_environment": (bundle / "environment").is_dir(),
                "task_manifest_digest": sha256_path(bundle / "task.toml"),
            }
        )
    return rows


def load_scope(root: Path | None = None) -> dict:
    base = root or project_root()
    path = base / AUDIT_DIRNAME / SCOPE_FILENAME
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def scope_binding(root: Path | None = None) -> dict:
    """Recompute the approved scope digest binding.

    Phase 1 item 1 requires this recomputation before any harness file is trusted,
    and Phase 2 item 2 requires the refusal on a missing or mismatched approval to
    be provable as a selfcheck row, so the comparison is exposed as data.
    """
    audit = (root or project_root()) / AUDIT_DIRNAME
    scope_path = audit / SCOPE_FILENAME
    approved_path = audit / SCOPE_APPROVED_FILENAME
    capabilities_path = audit / CAPABILITIES_FILENAME
    live = sha256_path(scope_path) if scope_path.exists() else None
    approved = approved_path.read_text(encoding="utf-8").strip() if approved_path.exists() else None
    return {
        "scope_present": scope_path.exists(),
        "approved_present": approved_path.exists(),
        "live_digest": live,
        "approved_digest": approved,
        "matches": bool(live and approved and live == approved),
        "capabilities_digest": sha256_path(capabilities_path)
        if capabilities_path.exists()
        else None,
    }


def collect(root: Path | None = None) -> Recon:
    base = root or project_root()
    _, sha = _git(base, "rev-parse", "HEAD")
    _, branch = _git(base, "rev-parse", "--abbrev-ref", "HEAD")
    status_code, status = _git(base, "status", "--porcelain")
    entries = [line for line in status.splitlines() if line.strip()] if status_code == 0 else []
    _, depth_text = _git(base, "rev-list", "--count", "HEAD")
    try:
        depth = int(depth_text)
    except ValueError:
        depth = 0
    return Recon(
        root=base,
        git_sha=sha,
        branch=branch,
        dirty_bit=bool(entries),
        dirty_entries=entries,
        history_depth=depth,
        runtime=collect_runtime(),
        binaries=collect_binaries(),
        scanner_databases=collect_scanner_databases(base),
        bundles=collect_bundles(base),
        scope=scope_binding(base),
    )


def _utc_now() -> str:
    return datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat()


__all__ = [
    "Recon",
    "SCANNER_BINARIES",
    "collect",
    "collect_binaries",
    "collect_bundles",
    "collect_runtime",
    "collect_scanner_databases",
    "load_scope",
    "scope_binding",
]
