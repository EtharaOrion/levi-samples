<p align="center"><img src="images/hero.svg" alt="LEVI" width="720"></p>

# LEVI: samples

<p align="center"><b>The samples lane: 3 of 30 Harbor task bundles.</b></p>

<p align="center"><a href="#summary"><img src="https://img.shields.io/badge/bundles-3_of_30-845EF7" alt="bundles: 3 of 30"></a> <a href="#evidence-status"><img src="https://img.shields.io/badge/sealed-0-845EF7" alt="sealed: 0"></a> <a href="#difficulty-tiers"><img src="https://img.shields.io/badge/difficulty-measured-845EF7" alt="difficulty: measured"></a></p>

<p align="center"><sub><a href="#abstract">Abstract</a> | <a href="#summary">Summary</a> | <a href="#difficulty-tiers">Difficulty tiers</a> | <a href="#evidence-status">Evidence status</a> | <a href="#coverage">Coverage</a> | <a href="#dataset-structure">Dataset structure</a> | <a href="#verification-and-quality-assurance">Verification and quality assurance</a> | <a href="#reproduction">Reproduction</a> | <a href="#cite">Cite</a> | <a href="#license">License</a> | <a href="#contact">Contact</a></sub></p>

## Abstract

The curated lane of this corpus: at most 30 Harbor task bundles, every anchor seated first and every other bundle in seal order. Bundles past that ceiling live in `delivery/`.

Each bundle is one Harbor task in a directory named by its content-derived uuid5, so the name doubles as an integrity check. This page is rendered from the resident bundles on every reconcile; a value a bundle does not carry reads `absent`, and the page never fills one in.

## Summary

| Property | Value |
| --- | --- |
| Bundles | 3 of 30 |
| Sealed | 0 of 3 |
| Registrations | adopted (3) |
| Audit verdicts | none (3) |
| Harbor schema | 1.4 (3) |

## Difficulty tiers

Difficulty is measured by the signed pilot alone and never declared in a bundle, so this page states no tier a bundle claims.

## Evidence status

The verdict is the audit outcome recorded at the sealed digest, and `none` means no verdict has landed for that digest yet. Only an authoring run removes a bundle from this lane, so removal waits for the next one.

| uuid | Verdict | Sealed digest | Stream |
| --- | --- | --- | --- |
| 4c7b8d6f-c500-585d-b7b2-3519df55b1b3 | none | absent | none |
| 6bf0c918-e9ad-5397-bb76-cf3e238f2df1 | none | absent | none |
| 873914cf-93b2-57a0-a5c8-264bfa2d3b66 | none | absent | none |

## Coverage

| Keyword | Bundles |
| --- | --- |
| issue-resolving | 3 |
| agent:openhands-sdk | 2 |
| python | 2 |
| reflex | 2 |
| mise | 1 |
| rust | 1 |

## Dataset structure

| Bundle | Task | Keywords | Registration | Sealed at | Tier |
| --- | --- | --- | --- | --- | --- |
| [`4c7b8d6f-c500-585d-b7b2-3519df55b1b3`](4c7b8d6f-c500-585d-b7b2-3519df55b1b3/) | `levi/s01-mise` | issue-resolving, mise, rust | adopted | unsealed | - |
| [`6bf0c918-e9ad-5397-bb76-cf3e238f2df1`](6bf0c918-e9ad-5397-bb76-cf3e238f2df1/) | `levi/t15-reflex` | agent:openhands-sdk, issue-resolving, python, reflex | adopted | unsealed | - |
| [`873914cf-93b2-57a0-a5c8-264bfa2d3b66`](873914cf-93b2-57a0-a5c8-264bfa2d3b66/) | `levi/t06-reflex` | agent:openhands-sdk, issue-resolving, python, reflex | adopted | unsealed | - |

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#131a33","primaryTextColor":"#e8ecff","primaryBorderColor":"#845EF7","lineColor":"#22d3ee","fontFamily":"monospace"}}}%%
flowchart LR
    bundle["&lt;uuid&gt;/"]
    bundle --> n0["task.toml<br/>runner manifest"]
    bundle --> n1["instruction.md<br/>objective the agent reads"]
    bundle --> n2["environment/<br/>agent sandbox image"]
    bundle --> n3["tests/<br/>verifier, hidden from the agent"]
    bundle --> n4["solution/<br/>private oracle"]
    bundle --> n5["trajectories/"]
```

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#131a33","primaryTextColor":"#e8ecff","primaryBorderColor":"#845EF7","lineColor":"#22d3ee","fontFamily":"monospace"}}}%%
flowchart LR
    staging["staging/"]
    staging --> samples["samples/<br/>3 of 30"]
    samples --> delivery["delivery/<br/>0 of 10000"]
    delivery --> stock["stock/<br/>0 of 10000"]
```

## Verification and quality assurance

Each bundle's signed provenance carrier holds its screening roots, screening instant, and absolute expiry. Placement moves that carrier into the private derivation set, which this page never reads, so reconcile lists no root it cannot verify here.

## Reproduction

Each bundle directory is a complete Harbor task: `task.toml` is the runner manifest, `instruction.md` the objective, `environment/` the sandbox image, and `tests/` the verifier. Point a Harbor runner at one bundle directory to reproduce it; `solution/` stays private.

## Cite

```bibtex
@misc{levi2026,
  title        = {LEVI: Long-Horizon Software Engineering Tasks from Real Merged Pull Requests},
  author       = {{Ethara.AI}},
  year         = {2026},
  howpublished = {\url{https://github.com/EtharaOrion/levi}}
}
```

## License

MIT. See [`LICENSE`](LICENSE).

## Contact

[Ethara.AI](https://github.com/Ethara-Ai), disclosures per [`SECURITY.md`](SECURITY.md), contributions per [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## Copyright

Copyright (c) 2026 Green Rider Technology LLP (Ethara AI). All rights reserved.
