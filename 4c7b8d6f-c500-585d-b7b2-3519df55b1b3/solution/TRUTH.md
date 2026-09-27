# TRUTH.md - jdx__mise-span:6c24088

GENERATED SECTION. DO NOT HAND-EDIT.

# FORGE canary block. Derived from the canonical content hash.
# FORGE-CANARY[00]=B0DA1BB6B34BE74C93CD24280FEE65D6
# FORGE-CANARY[01]=8586660CB375ACFF276580D9DBA47D08
# FORGE-CANARY[02]=120499FC16D16514990912FCD40AF63E
# FORGE-CANARY[03]=BD5FA149AC965B38CFB3268C11D80B60

## Defect

The .NET backend in mise can only install full SDKs; there is no way for a user to request a runtime-only install of a specific .NET framework. There is no inline `runtime` tool option accepted from either the command-line side bracket syntax or the tools table of a config file, no validation restricting values to the recognized framework names, no plumbing to make the install fetch a runtime instead of an SDK, and no correct uninstall path for runtime layouts. Additionally, the SDK sanity check runs unconditionally after install, which would fail on a valid runtime, and the uninstall deduplication logic discards the entry carrying tool options in favor of a plain filesystem match, so options never reach the uninstall logic.

The reference change touches 83 source file(s) in rust across 533 hunk(s). 5 target test(s) observe the result and 545 preserve target(s) must keep passing.

## Load-bearing work

The reference change lands in these files:

- `.github/workflows/auto-draft-pr.yml`
- `.github/workflows/docker.yml`
- `.github/workflows/release.yml`
- `.github/workflows/semantic-pr-lint.yml`
- `.github/workflows/vendored-file-warning.yml`
- `CHANGELOG.md`
- `Cargo.lock`
- `Cargo.toml`
- `README.md`
- `bun.lock`
- `completions/_mise`
- `completions/mise.bash`
- `completions/mise.fish`
- `completions/mise.ps1`
- `crates/aqua-registry/Cargo.toml`
- `crates/aqua-registry/aqua-registry/pkgs/ahkohd/oyo/registry.yaml`
- `crates/aqua-registry/aqua-registry/pkgs/bellicose100xp/jiq/registry.yaml`
- `crates/aqua-registry/aqua-registry/pkgs/kurama/dealve-tui/registry.yaml`
- `crates/aqua-registry/aqua-registry/pkgs/micahkepe/jsongrep/registry.yaml`
- `crates/aqua-registry/aqua-registry/pkgs/sigstore/cosign/registry.yaml`
- `crates/aqua-registry/aqua-registry/pkgs/textfuel/lazyjira/registry.yaml`
- `crates/aqua-registry/aqua-registry/pkgs/ubugeeei/vize/registry.yaml`
- `crates/vfox/Cargo.toml`
- `crates/vfox/src/hooks/backend_exec_env.rs`
- `crates/vfox/src/hooks/backend_install.rs`
- `crates/vfox/src/hooks/backend_list_versions.rs`
- `crates/vfox/src/vfox.rs`
- `default.nix`
- `deny.toml`
- `docs/.vitepress/theme/custom.css`
- `docs/backend-plugin-development.md`
- `docs/configuration.md`
- `docs/dev-tools/backends/npm.md`
- `docs/dev-tools/index.md`
- `docs/dev-tools/mise-lock.md`
- `docs/lang/dotnet.md`
- `docs/paranoid.md`
- `docs/tasks/file-tasks.md`
- `docs/tasks/task-arguments.md`
- `docs/tasks/task-configuration.md`

What each file must end up doing is declared in `rubrics.json`, which is what the deterministic channel reads. This section names the files so a reader knows the shape of the work, not the text to type.

## Verification

Apply the committed test patch, run the target set recorded in `tests/config.json` (5), and confirm the preserve set (545) still passes.

## Ordered plan

1. Locate the .NET backend and the request-option plumbing, and identify where ToolVersion options are read so a `runtime` key can be extracted from both the side bracket and tools-table forms.
2. Add validation that accepts only `dotnet`, `aspnetcore`, and `windowsdesktop` and returns a clear error for any other value, wired in early so invalid values never reach the install script.
3. Branch the install routine so that a valid runtime uses the platform-appropriate dotnet-install runtime selector for the given framework and version on both Unix and Windows, leaving the SDK path unchanged when no runtime is set.
4. Skip the post-install SDK version-command sanity check when a runtime install was performed, keeping it intact for SDK installs.
5. Compute the framework-and-version runtime directory layout for installed-file listing and for uninstall when a runtime was requested, and keep the SDK layout otherwise.
6. Fix the uninstall version deduplication so the option-bearing ToolVersion survives collapse instead of a bare filesystem match, without altering the resulting version set for optionless tools.
7. Update the .NET language documentation to describe runtime-only installs, the valid values, and both the command-line and config-file request forms.
8. Regenerate any derived artifacts such as shell completions and the JSON schema so they reflect the new option.
9. Run the five target tests and the full preserved suite to confirm the feature works and nothing regresses.

## Human-review residue

Item 10f requires every human-review item to name the semantic residue that blocks compilation. The rubric item schema is closed at eight fields, so the residue is recorded here rather than as a ninth field the schema does not admit.

- `R1`: The compiled surface is keyed on load-bearing sites and fair-play gates rather than on rubric item identifiers, so this item has no compiled counterpart to reduce to. The residue is the whole judgment.
- `R2`: The compiled surface is keyed on load-bearing sites and fair-play gates rather than on rubric item identifiers, so this item has no compiled counterpart to reduce to. The residue is the whole judgment.
- `R3`: The compiled surface is keyed on load-bearing sites and fair-play gates rather than on rubric item identifiers, so this item has no compiled counterpart to reduce to. The residue is the whole judgment.
- `R4`: The compiled surface is keyed on load-bearing sites and fair-play gates rather than on rubric item identifiers, so this item has no compiled counterpart to reduce to. The residue is the whole judgment.
- `R5`: The compiled surface is keyed on load-bearing sites and fair-play gates rather than on rubric item identifiers, so this item has no compiled counterpart to reduce to. The residue is the whole judgment.
- `R6`: The compiled surface is keyed on load-bearing sites and fair-play gates rather than on rubric item identifiers, so this item has no compiled counterpart to reduce to. The residue is the whole judgment.

## Rejected routes

- {'bound_control': 'controls.check_empty_submission', 'route': 'submit nothing and let the preserve suite carry the score', 'why_rejected': 'An empty submission leaves every fail-to-pass target unresolved and must score exactly zero under the bound reward schema.'}
- {'bound_control': 'controls.check_oracle_submission', 'route': 'submit a change that only appears to differ from no change', 'why_rejected': 'The oracle submission and the empty submission must differ; a bundle where they do not has a reward channel that cannot tell them apart.'}
- {'bound_control': 'controls.check_judged_inputs', 'route': 'reach the graded outcome by reading a judged input rather than by changing world state', 'why_rejected': 'Judged inputs are checked for the private carriers they must never contain, so a route that answers from them rather than from the environment is rejected.'}

## Provenance

```json
{
  "attestation_state": "unavailable",
  "base_commit_sha": "e26b4e78d9391891b38f3cce2cc34f2f9d0d0396",
  "instance_identity": "jdx/mise v2026.4.3..v2026.4.4",
  "license": "MIT",
  "number_interval": "8524-8598-8599-8750-8776-8849-8851-8857-8874-8875-8876-8881-8882-8884-8886-8887-8888-8889-8892-8893-8894-8896-8897-8898-8899-8900-8901-8903-8904-8905-8906-8908-8909-8910-8911-8912-8913-8914-8915-8916-8917-8918",
  "origin": "derived",
  "provenance_date": "2026-04-04T23:23:38Z",
  "repository": "jdx/mise",
  "repository_canonical_identity": "R_kgDOIvux3g",
  "source_kind": "public_repository",
  "span_label": "v2026.4.3..v2026.4.4"
}
```
