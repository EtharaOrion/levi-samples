"""Private recomputation script for one Trinity task bundle.

Derives every generated canonical artifact of this bundle from
`solution/grounding.yaml`: the executable oracle, the human-readable ground
truth, the reference-based rubric, and the compiled deterministic rubric tests.
They come from one source so the oracle, the truth, the rubric, and the tests
cannot disagree with each other.

This script invokes no model, no network, no clock, no locale, and no random
source. Every string it emits is either a literal frozen in the grounding source
or a fixed template here, so two hosts that differ in hostname, working
directory, user, and environment produce identical bytes. `grounding.yaml` is a
single JSON document, which is valid YAML 1.2, so reading it needs only the
standard library and no parser whose version could change the result.
"""

from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
BANNER = "GENERATED SECTION. DO NOT HAND-EDIT."


def load():
    with open(os.path.join(HERE, "grounding.yaml"), encoding="utf-8") as handle:
        return json.load(handle)


def canary_block(g):
    return "\n".join(
        "FORGE-" + "CANARY[%02d]=%s" % (index, value)
        for index, value in enumerate(g["canary_values"])
    )


def canary(g):
    lines = ["# FORGE canary block. Derived from the canonical content hash."]
    for line in canary_block(g).splitlines():
        lines.append("# " + line)
    return "\n".join(lines)


def write(path, text, executable=False):
    full = os.path.join(BUNDLE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    if executable:
        os.chmod(full, 0o755)


def solve_sh(g):
    return "\n".join([
        "#!/bin/bash",
        "# Executable oracle. Applies the reference solution and commits it, because a test",
        "# suite that inspects the working tree must see a clean one.",
        "set -euo pipefail",
        "",
        'cd "%s"' % g["workdir"],
        "# The workspace may be bind-mounted, in which case its ownership differs from the",
        "# running user and git refuses to touch it. Declaring it safe is not a relaxation of",
        "# anything the policy manifest denies: it is what makes the oracle behave the same",
        "# whether the tree lives in the image or is mounted into it.",
        'git config --global --add safe.directory "%s" || true' % g["workdir"],
        "git apply --whitespace=nowarn /solution/fix.patch",
        "git add -A",
        'git -c user.email=oracle@trinity.invalid -c user.name="Trinity Oracle" \\',
        '    commit -q --no-verify -m "reference solution" || true',
        "",
    ])


def truth_md(g):
    out = ["# TRUTH.md - %s" % g["instance_id"], "", BANNER, "", canary(g), "", "## Defect", ""]
    out.append(g["defect"])
    out.append("")
    out.append("The reference change touches %d source file(s) in %s across %d hunk(s). %d target "
               "test(s) observe the result and %d preserve target(s) must keep passing."
               % (g["source_files"], g["language"], g["source_hunks"],
                  len(g["f2p_tests"]), len(g["p2p_tests"])))
    out += ["", "## Load-bearing work", ""]
    out.append("The reference change lands in these files:")
    out.append("")
    for path in g["load_bearing_paths"]:
        out.append("- `%s`" % path)
    out += ["", "What each file must end up doing is declared in `rubrics.json`, which is what the "
            "deterministic channel reads. This section names the files so a reader knows the "
            "shape of the work, not the text to type.", ""]
    out += ["## Verification", ""]
    out.append("Apply the committed test patch, run the target set recorded in `tests/config.json` "
               "(%d), and confirm the preserve set (%d) still passes."
               % (len(g["f2p_tests"]), len(g["p2p_tests"])))
    out += ["", "## Ordered plan", ""]
    for i, step in enumerate(g["ordered_plan"], start=1):
        out.append("%d. %s" % (i, step))
    out += ["", "## Human-review residue", ""]
    out.append("Item 10f requires every human-review item to name the semantic residue that blocks "
               "compilation. The rubric item schema is closed at eight fields, so the residue "
               "is recorded here rather than as a ninth field the schema does not admit.")
    out.append("")
    for item in g["rubric_items"]:
        if item["mode"] == "human_review":
            out.append("- `%s`: %s" % (item["id"], item.get("semantic_residue", "unnamed")))
    out += ["", "## Rejected routes", ""]
    for route in g["rejected_routes"]:
        out.append("- %s" % route)
    out += ["", "## Provenance", "", "```json"]
    out.append(json.dumps(g["provenance_summary"], indent=2, sort_keys=True))
    out += ["```", ""]
    return "\n".join(out)


def rubrics_json(g):
    items = []
    for item in g["rubric_items"]:
        items.append({
            "id": item["id"],
            "dimension": item["dimension"],
            "weight": item["weight"],
            "evaluation_target": item["evaluation_target"],
            "criterion": item["criterion"],
            "evaluation_rule": item["judgment"],
            "evidence": item["evidence"],
            "mode": item["mode"],
        })
    doc = {
        "source": "generated by solution/recompute.py from solution/grounding.yaml",
        "schema_note": "The item schema is closed at eight fields. The semantic residue that "
                       "blocks compilation for each human-review item is recorded in TRUTH.md, "
                       "because a ninth field here would break the closed schema.",
        "compilation_floor_note": g["compilation_floor_note"],
        "canary_block": canary_block(g),
        "items": items,
    }
    return json.dumps(doc, indent=2, sort_keys=True) + "\n"


def _slug(text):
    out = re.sub(r"[^0-9a-zA-Z]+", "_", str(text)).strip("_").lower()
    return re.sub(r"_+", "_", out)


def test_output_py(g):
    """The task-specific deterministic channel, emitted from grounding.yaml.

    This channel exists because a run can satisfy every fail-to-pass target and still
    miss every load-bearing site the reference change touched. The outcome channel
    cannot see that; this one can.

    It embeds site paths, requirement identifiers and requirement descriptions and
    nothing else. Probe literals stay in tests/rubrics.json and are loaded at run
    time, so no reference text reaches this module, which item 10f forbids because the
    verifier surface is agent-reachable after the run.

    It is self-contained on purpose. The assay emitter resolves its engine by walking
    parents for an importable assay package; under samples/<uuid>/ no such parent
    exists, so a verbatim port would emit a module that cannot import. This reads the
    evidence the verifier already writes: final.diff and summary.json under LOGS.
    """
    sites = g.get("sites") or []
    reqs = [(st, r) for st in sites for r in (st.get("requirements") or [])]
    unobserved = [r for _, r in reqs if not r.get("load_bearing")]
    observed = [r for _, r in reqs if r.get("load_bearing")]
    out = [
        '"""Deterministic process checks for %s.' % g["instance_id"],
        "",
        "Generated by solution/recompute.py from solution/grounding.yaml. %d load-bearing"
        % len(sites),
        "site(s), %d requirement(s) a target test already observes and %d it does not."
        % (len(observed), len(unobserved)),
        "",
        "Hard gates assert. Requirement and site outcomes are recorded rather than",
        "asserted: this module's job is to produce a score and a readable checklist, and",
        "failing every imperfect run would destroy both.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "import json",
        "import os",
        "",
        "import pytest",
        "",
        "LOGS = os.environ.get('TRINITY_LOGS', '/logs/verifier')",
        "HERE = os.path.dirname(os.path.abspath(__file__))",
        "TASK_DIR = os.path.dirname(HERE)",
        "# Derived from where the module lives rather than embedded. The uuid is a function",
        "# of the canonical hash and this file is inside that hash, so embedding it would be",
        "# circular; reading it from the directory also means the module cannot disagree",
        "# with the bundle it ships in.",
        "TASK_UUID = os.path.basename(TASK_DIR)",
        "INSTANCE_ID = %r" % g["instance_id"],
        "",
        "",
        "def reward():",
        "    # reward.json carries numeric values only, because Harbor rejects the whole",
        "    # object if any value is a string. The reason lives beside it.",
        "    with open(os.path.join(LOGS, 'reward.json'), encoding='utf-8') as handle:",
        "        record = json.load(handle)",
        "    path = os.path.join(LOGS, 'reward_reason.json')",
        "    if os.path.exists(path):",
        "        with open(path, encoding='utf-8') as handle:",
        "            record = dict(json.load(handle), **record)",
        "    return record",
        "",
        "",
        "def summary():",
        "    path = os.path.join(LOGS, 'summary.json')",
        "    if not os.path.exists(path):",
        "        pytest.skip('the graded run recorded no structural summary')",
        "    with open(path, encoding='utf-8') as handle:",
        "        return json.load(handle)",
        "",
        "",
        "def submission_diff():",
        "    path = os.path.join(LOGS, 'final.diff')",
        "    if not os.path.exists(path):",
        "        pytest.skip('the graded run recorded no submission diff')",
        "    with open(path, encoding='utf-8', errors='replace') as handle:",
        "        return handle.read()",
        "",
        "",
        "def touched_paths():",
        "    import re as _re",
        "    text = submission_diff()",
        r"    return set(_re.findall(r'^\+\+\+ b/(.+)$', text, _re.M))",
        "",
        "",
        "def rubric_probes():",
        "    # Probe literals live in rubrics.json, never in this module.",
        "    with open(os.path.join(TASK_DIR, 'tests', 'rubrics.json'), encoding='utf-8') as h:",
        "        doc = json.load(h)",
        "    out = {}",
        "    for site in doc.get('sites') or []:",
        "        for req in site.get('requirements') or []:",
        "            out[req['id']] = (site.get('path'), req.get('probe') or {})",
        "    return out",
        "",
        "",
        "def probe_satisfied(req_id):",
        "    path, probe = rubric_probes().get(req_id, (None, {}))",
        "    text = submission_diff()",
        "    any_of = probe.get('any_of') or []",
        "    if not any_of:",
        "        return path in touched_paths() if path else False",
        "    return any(frag and frag in text for frag in any_of)",
        "",
        "",
        "def test_reward_is_written_and_in_range():",
        "    value = reward()['reward']",
        "    assert 0.0 <= value <= 1.0",
        "",
        "",
        "def test_every_zero_carries_a_machine_readable_reason():",
        "    record = reward()",
        "    if record['reward'] == 0.0:",
        "        assert record.get('reason'), 'a zero score must name its reason'",
        "",
        "",
        "class TestFairPlay:",
        '    """Hard gates. A failure here voids the run outright.',
        "",
        "    Two of the four gates the delivery corpus emitter carries are absent here and",
        "    named rather than faked: no-upstream-content-fetched and no-oracle-path-read",
        "    need egress and access telemetry, and nothing the bundle itself writes records",
        "    either. Closing them needs the runner under harness/ to record them, which is",
        "    read-only to this instrument.",
        '    """',
        "",
        "    def test_graded_tests_were_not_rewritten(self):",
        "        reason = reward().get('reason') or ''",
        "        assert reason != 'submission-modified-the-verifier-tree', reason",
        "",
        "    def test_the_run_and_the_bundle_agree(self):",
        "        declared = %d" % len(g.get("f2p_tests") or []),
        "        observed = summary().get('f2p_total', summary().get('targets_total'))",
        "        assert observed == declared, (",
        "            'the run graded ' + str(observed) + ' targets and the bundle declares '",
        "            + str(declared))",
        "",
        "",
        "class TestReachedTheLoadBearingSites:",
        '    """One node per site the reference change touches. Recorded, not asserted.',
        "",
        "    A run can satisfy every fail-to-pass target without reaching any of these,",
        "    which is the whole reason this channel is separate from the outcome channel.",
        '    """',
        "",
    ]
    if not sites:
        out += ["    def test_none_declared(self):",
                "        pytest.skip('grounding declares no load-bearing site')", ""]
    seen = {}
    for site in sites:
        base = _slug(os.path.splitext(os.path.basename(site["path"]))[0])
        seen[base] = seen.get(base, 0) + 1
        name = base if seen[base] == 1 else "%s_%d" % (base, seen[base])
        out += [
            "    def test_reached_%s(self, record_property):" % name,
            "        %r" % site["path"],
            "        reached = %r in touched_paths()" % site["path"],
            "        record_property(%r, 'reached' if reached else 'not-reached')"
            % ("E1-touched:%s" % site["path"]),
            "",
        ]
    out += [
        "",
        "class TestRequirementsTheOutcomeChannelCannotSee:",
        '    """Scored here, because no fail-to-pass or none-to-pass test observes them.',
        "",
        "    These are the whole reason the deterministic channel exists: a run can",
        "    satisfy every target test and still miss all of them.",
        '    """',
        "",
    ]
    if not unobserved:
        out += ["    def test_none_declared(self):",
                "        pytest.skip('rubrics.json declares no unobserved requirement')", ""]
    for req in unobserved:
        out += [
            "    def test_%s(self, record_property):" % _slug(req["id"]),
            "        %r" % " ".join(str(req.get("description", "")).split()),
            "        ok = probe_satisfied(%r)" % req["id"],
            "        record_property(%r, 'met' if ok else 'unmet')"
            % ("E2-req:%s" % req["id"]),
            "        assert ok, %r" % ("site requirement %s is not satisfied by final.diff" % req["id"]),
            "",
        ]
    out += [
        "",
        "class TestRequirementsAlreadyPricedByTheOutcomeChannel:",
        '    """Recorded only. The outcome channel already scores these through its',
        "    fail-to-pass targets, so weighting them here would pay for one fact twice.",
        '    """',
        "",
    ]
    if not observed:
        out += ["    def test_none_declared(self):",
                "        pytest.skip('rubrics.json declares no observed requirement')", ""]
    for req in observed:
        out += [
            "    def test_%s_is_recorded_not_scored(self, record_property):" % _slug(req["id"]),
            "        %r" % " ".join(str(req.get("description", "")).split()),
            "        ok = probe_satisfied(%r)" % req["id"],
            "        record_property(%r, 'met' if ok else 'unmet')"
            % ("E2-req:%s" % req["id"]),
            "",
        ]
    out += [
        "",
        "class TestTheScoreIsUsable:",
        "    def test_score_is_well_formed(self):",
        "        assert 0.0 <= reward()['reward'] <= 1.0",
        "",
        "    def test_the_run_produced_a_submission(self):",
        "        assert submission_diff().strip(), 'the run recorded an empty submission'",
        "",
    ]
    return "\n".join(out)


def main():
    g = load()
    write("solution/solve.sh", solve_sh(g), executable=True)
    write("solution/TRUTH.md", truth_md(g))
    write("solution/rubrics.json", rubrics_json(g))
    write("tests/test_output.py", test_output_py(g))
    print("regenerated 4 artifacts from grounding.yaml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
