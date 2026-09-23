---
name: rig
description: "FORGE harness operator door. Runs the inference and evaluation entry points of the harness/ benchmark extension over resident bundles as an author-side probe, never as difficulty evidence. USE FOR: running harness/ inference locally, evaluating a rollout log against a bundle's own tests, smoke-checking the benchmark extension, recording .seed/probe.yaml entries."
---

# rig

Rig is the operator door for `harness/`, the benchmark extension FORGE alone generates under item 1b. It runs the harness's inference and evaluation entry points over resident bundles, scoring through each bundle's own `tests/` under the pinned Harbor release with no grading logic of its own. Every run it makes is an author-side `.seed/probe.yaml` record, never difficulty evidence. It never writes `.seed/proof.yaml`, which only the out-of-band Phase 4 runner produces, and never mounts `solution/` where the agent can see it.

`trinity/FORGE.md` is the authority for what this door binds and when it runs. A lane loading this skill reads it at `### Phase 1: construct or reconcile the task bundle` alone and follows it, and only the orchestrating run reads it whole; this door adds nothing to it and restates none of it.

Run the parent gate at both moments, before any phase work and again before the root report, from the parent project root, the directory whose direct child is the `trinity/` submodule:

    just --justfile trinity/tools/justfile parent-gate instrument=FORGE moment=preflight
    just --justfile trinity/tools/justfile parent-gate instrument=FORGE moment=report
