---
description: Run the ENGRAM Phase H fold lane over signed instrument evidence.
---

Read `trinity/ENGRAM.md` and run the Phase H fold lane: admit every signed envelope waiting at the proof boundary, fold the signed groups and the FORGE-emitted design records the lane names, and publish the epoch. Operate from the parent project root, resolve every bare path there, and follow the contract end to end; this door defers to it, adds nothing to it, and restates none of it.

Run the parent gate at both moments, before any phase work and again before the root report, from the parent project root, the directory whose direct child is the `trinity/` submodule:

    just --justfile trinity/tools/justfile parent-gate instrument=ENGRAM moment=preflight
    just --justfile trinity/tools/justfile parent-gate instrument=ENGRAM moment=report
