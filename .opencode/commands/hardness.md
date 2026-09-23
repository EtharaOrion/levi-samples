---
description: Run the ENGRAM Phase H research lane over the published hardness corpus.
---

Read `trinity/ENGRAM.md` and run the Phase H research lane: research the published hardness corpus, reconcile the hardness contract, and regenerate `HARDNESS.md` from `.memory/hardness.yaml`. Operate from the parent project root, resolve every bare path there, and follow the contract end to end; this door defers to it, adds nothing to it, and restates none of it.

Run the parent gate at both moments, before any phase work and again before the root report, from the parent project root, the directory whose direct child is the `trinity/` submodule:

    just --justfile trinity/tools/justfile parent-gate instrument=ENGRAM moment=preflight
    just --justfile trinity/tools/justfile parent-gate instrument=ENGRAM moment=report
