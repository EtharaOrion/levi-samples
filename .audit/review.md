# CRUCIBLE Phase 2 review instructions

## What you may read

You may read exactly two files: `.audit/evidence.yaml` and this file. You may not read a bundle, a rollout, a source file, a scanner output, a git object, or any live code. You may not restate a claim you cannot locate inside `.audit/evidence.yaml`. If a statement you want to write is not grounded in a row of that document, you do not write it.

The evidence document is the only citable source because every instrument in it recorded its own argv, exit code, raw artifact digests, and both-halves standing at the moment it ran. A claim traced to anything else is a claim no reviewer can re-derive.

## What the document contains

`.audit/evidence.yaml` carries `schema: crucible.evidence/v1` and these keys.

`recon` records the git SHA, the dirty bit, the resolved bundle set, the runtime, the scanner binary inventory, the scanner database pin states, and the scope binding. `scope_digest` binds the approved scope; `disposition` carries the harness-computed cap over every instrument.

`instruments` holds one row per instrument. Each row carries `instrument`, `ran`, `standing`, `disposition_cap`, `findings`, `coverage_gaps`, `raw_artifacts`, and `notes`. `ran: false` means the instrument did not execute; read its gaps to learn why. `standing` is three-valued and is never a pass or fail: `observed_violation` means a violation was seen, `demonstrated_coverage` means coverage was proven and no violation was found, and `insufficient_evidence` means the question was not answerable from committed bytes.

`findings` holds every retained finding sorted by critical class then id. Each carries `finding_id`, `instrument`, `critical_class`, `severity`, `caps`, `bucket`, `subject`, `statement`, and `evidence`. `caps` is the disposition the finding imposes and is one of `BLOCK`, `HOLD`, or `SHIP`. `bucket` is `deterministic` for a harness-computed result and `semantic` for a judged one.

`coverage_gaps` holds every gap sorted by id. Each carries `gap_id`, `instrument`, `surface`, `subject`, `reason`, `caps`, and `statement`. A gap always caps at HOLD or below and is never converted into a judgement.

`normalized_issues` and `issue_identity_multiset` carry content-anchored issue identities that survive formatting drift.

`reward_coverage_ledger` carries `reward_claim_model_version`, `capability_vocabulary_version`, `rows`, and `unresolved_rows`. Each row resolves as exactly `detected`, `externally_enforced`, `not_applicable`, or `gap`. A `detected` row names the live atom. A `not_applicable` row carries the derivation CRUCIBLE computed from the committed closure; a producer declaration is never accepted in its place.

## How to reason

Deterministic evidence governs. A judged conclusion may lower a disposition and may identify a defect, but it may never raise a disposition above what the deterministic rows support, and it may never certify that something is absent. Where an instrument reports `insufficient_evidence`, that is a gap and not a pass.

An instrument that did not run is not evidence of cleanliness. Read whether its absence carries a gap capping HOLD or a finding capping BLOCK, and report the cap the document records rather than the cap you would prefer.

A clean screen never proves absence. Say what was measured and against which pinned root, and say what remained unresolved.

Do not soften a BLOCK. If the document computes BLOCK, the verdict is BLOCK and the executive summary leads with the worst retained critical finding.

## What you write

Write `.audit/findings.yaml` inside the harness and `VERDICT.md` at the repository root.

`VERDICT.md` carries exactly six `##` sections, each appearing exactly once, in this order: Executive summary, Disposition, Findings, Coverage gaps, Escalations, Flag legend. An empty section reads `None.`

Executive summary leads with the worst retained critical finding, ordering 🔴 and ⛔ before 🟡 and ⚠️ before 🟢 and ✅, and closes with the gate summary.

Disposition carries the gate headline and nothing else on its first non-empty line: either `SHIP <bundle-set digest>` or `HOLD` alone or `BLOCK` alone.

Findings nests every retained finding under its applicable critical class.

Coverage gaps carries every gap in the document, including missing-view, playbook, instrument, provenance, and execution-evidence gaps.

Escalations carries standing integrity priorities and any requirement discovered here that affects the next gate.

Flag legend defines the flags.

A mandatory table titled `Adversary probes` binds the measured adversarial probe rows with their measured scores and the rule each was judged against.

Flags appear in Markdown only: ✅ pass, ⚠️ coverage gap or stale or unverified claim, ⛔ critical or blocking defect, 🟢 SHIP, 🟡 HOLD, 🔴 BLOCK. YAML stays emoji-free and ASCII.

Prose carries no em-dashes and no hard line breaks inside a paragraph.

## Judge discipline

Any judged conclusion requires at least eleven trials, position randomization, conformal prediction sets, and a perturbation suite before it is admitted. A judge that fails perturbation testing is not deployed. Absent discipline caps the gate at HOLD. A low-confidence conformal call narrows a claim and never raises a disposition.
