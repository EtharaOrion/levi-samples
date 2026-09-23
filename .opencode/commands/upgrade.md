---
description: Run the FORGE Upgrade lane over the resident samples/<uuid>/ bundles the invocation names.
---

Read `trinity/FORGE.md` and run the Upgrade lane alone over the resident `samples/<uuid>/` paths the invocation names, authoring one successor per path under `staging/` and nothing else. Operate from the parent project root, resolve every bare path there, and follow the contract end to end; this door defers to it, adds nothing to it, and restates none of it.

Run the parent gate at both moments, before any phase work and again before the root report, from the parent project root, the directory whose direct child is the `trinity/` submodule:

    just --justfile trinity/tools/justfile parent-gate instrument=FORGE moment=preflight
    just --justfile trinity/tools/justfile parent-gate instrument=FORGE moment=report
