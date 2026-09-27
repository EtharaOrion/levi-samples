You are working in the Rust repository at `/workspace/mise`.

The .NET tooling in mise currently only knows how to install .NET SDKs. A user who wants a specific .NET runtime installed, either alongside an SDK or on its own, has no way to express that intent. The required behaviour is to let users request a runtime-only installation through an inline tool option named `runtime`, which selects which .NET framework to install rather than a full SDK. This option must be accepted both from the command line using the existing side bracket syntax on the tool name and from the tools table of a mise configuration file, where a version entry may carry the option as an additional key.

The `runtime` option must accept only the recognized .NET framework names, which are `dotnet`, `aspnetcore`, and `windowsdesktop`. Any other value must be rejected with a clear validation error rather than being passed through to the underlying install machinery. When a valid runtime value is present, the installation must instruct the .NET install process to fetch that runtime for the requested version instead of an SDK, honoring the platform-appropriate invocation on both Unix-like systems and Windows.

Because a runtime-only installation does not provide the SDK command surface, the post-install sanity check that confirms an SDK by invoking the .NET version command must not run for runtime installs, since it would otherwise fail on a perfectly good runtime. The installed files for a runtime live under a different directory layout than SDKs do, organized by framework and version rather than under the SDK path, and uninstalling a runtime must remove the correct runtime location for the chosen framework and version rather than attempting to remove an SDK that was never installed.

There is a related defect in uninstall handling that must be fixed for this to work end to end. When a tool is requested for uninstallation, the requested versions are gathered from more than one source, and duplicates are collapsed so that a version is only acted on once. Today the entry that carries the tool options can be discarded during that deduplication in favor of a plain filesystem match, which means the options a user specified never reach the uninstall logic. After the change, the entry that carries the resolved tool options must be the one that survives deduplication, so that a runtime uninstall targets the right path. This must not disturb the uninstall behaviour for ordinary tools and versions that carry no options.

This is an additive feature and not a breaking change. Installing and uninstalling .NET SDKs with no `runtime` option must continue to behave exactly as it does now, and all behaviour of other tools and backends must be unaffected. The user-facing documentation for the .NET language support should describe the new runtime-only capability, the set of valid values, and how to request it from both the command line and configuration files.

If the project ships generated artifacts such as shell completions or a configuration schema that are derived from the tool and option definitions, and the new option affects any of them, those generated outputs must be regenerated so they remain consistent with the source of truth.

The description below carries several separate issues. Every issue in it is in scope. Work through all of them.

## Issue 1

Pull request #8524: feat(dotnet): support runtime-only installs

Referencing discussion #8494

## Summary

Adds support for installing .NET runtimes alongside or instead of SDKs, via an inline tool option (`runtime`). Uses the existing backend-name side bracket syntax options.

## Usage

```sh
mise use dotnet[runtime=dotnet]@8.0.14
dotnet --list-runtimes
```

```toml
[tools]
dotnet = [ "9", { version = "8.0.14", runtime = "dotnet" } ]
```

Valid runtime values: `dotnet`, `aspnetcore`, `windowsdesktop`

## Changes

- **`src/plugins/core/dotnet.rs`**:
  - Validate the `runtime` option value against known framework names.
  - Pass `--runtime` / `-Runtime` to the install script when the option is set.
  - Skip `dotnet --version` post-install check for runtime installs.
  - Route runtime uninstall paths (`shared/<framework>/<version>` instead of `sdk/<version>`).
- **`src/cli/uninstall.rs`**:
  - Reorder `get_requested_tool_versions()` so `tvr.resolve()` (which carries tool options) is pushed before filesystem matches. The `unique_by` dedup keeps the first entry, so the options-bearing `ToolVersion` now wins instead of being silently dropped.
- **`e2e/core/test_dotnet`**: Add tests for runtime-only install and invalid runtime option validation.
- **`docs/lang/dotnet.md`**: Document the runtime-only install feature, valid values, and usage notes.

## Issue 2

Pull request #8598: refactor(go): rename go_* settings to go.* namespace

Rename all Go settings from flat `go_*` format to nested `go.*` namespace for consistency with other language settings (`node.*`, `python.*`, `ruby.*`).

Old setting names are preserved as deprecated aliases for backward compatibility.

### Changes
- `go_default_packages_file` → `go.default_packages_file`
- `go_download_mirror` → `go.download_mirror`
- `go_repo` → `go.repo`
- `go_set_gobin` → `go.set_gobin`
- `go_set_gopath` → `go.set_gopath`
- `go_set_goroot` → `go.set_goroot`
- `go_skip_checksum` → `go.skip_checksum`

Also adds documentation note about `MISE_GO_DEFAULT_PACKAGES_FILE` env var (original PR intent).

## Issue 3

Pull request #8599: fix(lock): prune stale version entries during filtered `mise lock <tool>` runs

## Summary

When running `mise lock <tool>` after a tool's resolved version changes, the old lockfile entry was preserved and a new one appended, resulting in duplicate `[[tools.<tool>]]` sections with different versions.

For example, if `mise.toml` has `node = "24"` and `mise.lock` previously resolved to `24.13.0`, then after `24.14.0` becomes available and is installed, running `mise lock node` produces:

```toml
[[tools.node]]
version = "24.13.0"
backend = "core:node"
# ... platform entries ...

[[tools.node]]
version = "24.14.0"
backend = "core:node"
# ... platform entries ...
```

The expected behavior is that `mise lock node` should replace the stale `24.13.0` entry with the `24.14.0` entry, not append alongside it.

## Cause

Two code locations interact to produce this bug:

1. **Filtered lock runs skip all pruning** ([`src/cli/lock.rs:168-176`](https://github.com/jdx/mise/blob/010812ac19e14101c9225221da534fd83a4e0060/src/cli/lock.rs#L168-L176)): `prune_stale_entries_if_needed()` returns early for filtered runs (`mise lock <tool>`) to avoid removing non-targeted tools. But this also prevents pruning old versions of the *targeted* tool itself.

2. **`set_platform_info` matches by `(version, options)`** ([`src/lockfile.rs:655-705`](https://github.com/jdx/mise/blob/010812ac19e14101c9225221da534fd83a4e0060/src/lockfile.rs#L655-L705)): a version change always creates a new entry rather than updating the existing one.

## Prior art

- **#5907** fixed this same class of bug for the `update_lockfiles()` code path used by `mise install`/`mise upgrade`. The `mise lock` CLI uses a separate code path that was not covered.
- **#8265** added pruning of stale entries to `mise lock`, but only for unfiltered runs and only by tool name (tools removed from config entirely), not by stale versions within a targeted tool.

## Fix

- Add `Lockfile::retain_tool_versions(short, keep_versions)` that removes entries for a tool whose version is not in the given set.
- Add `Lock::prune_stale_versions_for_targeted_tools()` that, for filtered runs only, collects the current resolved versions per tool and calls `retain_tool_versions` before processing.
- The existing guard against pruning non-targeted tools remains intact — only versions of the targeted tool(s) are pruned.

## Tests

- 4 unit tests covering: stale version pruned, current version preserved, non-targeted tools untouched, unfiltered runs skip this path.
- 1 e2e test (`test_lockfile_lock_filtered_prune_stale_versions`) verifying the end-to-end scenario.

## Issue 4

Pull request #8750: fix(python): use lockfile URL for precompiled installs

When installing precompiled Python, `install_precompiled` would always recompute the download URL from the remote version index, ignoring any URL already recorded in `mise.lock`. This broke reproducibility for locked installs.

Now checks `lock_platforms` for an existing URL before fetching remote versions. If found, uses it directly.

Fixes https://github.com/jdx/mise/discussions/8749

## Issue 5

Pull request #8776: feat(deps): add `depends` field for user-specified tool dependencies

Allow users to declare explicit installation dependencies between tools in mise.toml, ensuring one tool is fully installed before another starts.

- Addresses this discussion and comment: https://github.com/jdx/mise/discussions/5964#discussioncomment-14076783

> [!NOTE]
> This code in this PR was mainly AI-written. I understand the changes generally but I might be missing nuances since I don't know Rust or the Mise codebase very well. I intend to see the PR through, but feel free to close if it's too far away from workable (although I don't think it is).

## Issue 6

Pull request #8849: fix(backend): filter PEP 440 .dev versions in fuzzy version matching

## Summary
  - Fix `VERSION_REGEX` to filter PEP 440 `.dev` versions (e.g. `2026.3.3.162408.dev0`) during fuzzy version matching
  - The regex caught `-dev` (hyphen) but not `.dev` (dot), so dev versions incorrectly satisfied stable version requests
  - One-character fix: `-dev` → `[-\.]dev`, matching the existing pattern for `rc` and `pre`

  ## Test plan

  - [x] Unit test for `VERSION_REGEX` matching `.dev` versions
  - [x] E2E test with inline plugin verifying `mise latest`, `mise install`, and `mise exec` correctly distinguish stable from `.dev` versions
  - [x] Existing unit tests (390 passed)
  - [x] Existing e2e tests (`test_latest`, `test_ls_remote`) pass — no regressions

Fixes https://github.com/jdx/mise/discussions/8784

## Issue 7

Pull request #8851: feat(npm): apply install_before to transitive dependencies

## Summary
- validate the selected top-level `npm:` package version against the effective `install_before` cutoff and fail if it was released on or after that cutoff
- forward the same cutoff into transitive dependency resolution during install for all npm backend package managers

## Details
- exact `npm:<pkg>@<version>` installs no longer bypass `install_before`; they now fail closed when the selected version is newer than the cutoff
- transitive dependency age gating uses each package manager's native CLI form:
  - `npm`: `--before <timestamp>`
  - `bun`: `--minimum-release-age <seconds>`
  - `pnpm`: `--config.minimumReleaseAge=<minutes>`
- mise now forwards those package-manager-specific flags without a runtime version pre-check
- npm intentionally stays on `--before`, not `--min-release-age`, because npm implements `min-release-age` by translating it into `before`, and mise already has an exact timestamp cutoff

## Tests / docs
- add unit coverage for cutoff precedence, transitive CLI arg generation, and exact-version cutoff failures
- extend npm backend e2e coverage to assert the package-manager-specific transitive age-gating args
- update npm backend docs and `install_before` docs; `docs/tips-and-tricks.md` now points to the npm backend docs for package-manager-specific details
- rerun `mise run render`

## Question For Maintainer
I changed exact `npm:<pkg>@<version>` installs to fail closed when the selected top-level version is newer than `install_before`, instead of letting exact top-level versions through and only gating transitives. Is that the behavior you want merged, or would you prefer exact top-level versions to bypass the cutoff and apply it only to transitive dependencies?

## Notes
- `mise run render` completed with the existing cache write warnings under `/home/risu/.cache/mise/...` due to the read-only environment
- I also attempted focused `cargo test` verification, but this environment was unreliable about returning final harness completion after compiler subprocesses exited
- I manually tested older package manager versions with `mise x`; older `pnpm` and `bun` accepted the forwarded flags, while older `npm` still broke on `--before`, but this change intentionally removes the preflight version gate instead of enforcing runtime minimums in mise

Interface (names the hidden tests import; implementation is yours):
- `CLI flag --minimum-release-age`

## Issue 8

Pull request #8857: fix: when direnv diff is empty, do not try to parse it

I kept getting the following error every time mise started with direnv and mise in my `.zshrc`:

```
mise WARN  failed to update DIRENV_DIFF: EOF while parsing a value at line 1 column 0 
```

When the DIRENV_DIFF environment variable was empty, the parser would bail out and it was a spurious warning.

This makes mise ignore empty diff's (and adds some more debug logging to figure out *where* it was failing 😄)

## Issue 9

Pull request #8874: fix: update flake.lock and add fix for rust-bindgen to default.nix

This updates the flake.lock file as it was installing Rust 1.85 and several crates no longer support that version:

```shell
❯ nix develop
❯ mise run build
[build] $ cargo build --all-features
error: rustc 1.85.0 is not supported by the following packages:
  aws-config@1.8.12 requires rustc 1.88
  aws-credential-types@1.2.11 requires rustc 1.88
  aws-runtime@1.5.18 requires rustc 1.88
  aws-sdk-s3@1.121.0 requires rustc 1.88.0
...
```

This PR also adds `bindgenHook` to `default.nix` so that `bindgen` can work (see https://ryantm.github.io/nixpkgs/languages-frameworks/rust/#hooks):

```shell
❯ nix develop
❯ mise run build
[build] $ cargo build --all-features
 ...
error: failed to run custom build command for `aws-lc-sys v0.39.0`
...
  thread 'main' (116706) panicked at /var/home/esteve/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/bindgen-0.72.1/lib.rs:616:27:
  Unable to find libclang: "the `libclang` shared library at /usr/lib64/llvm21/lib64/libclang.so.21.1.8 could not be opened: libLLVM.so.21.1: cannot open shared object file: No such file or directory"
  note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
warning: build failed, waiting for other jobs to finish...
[build] ERROR task failed
```

## Issue 10

Pull request #8875: feat: add options field to BackendListVersionsCtx

This PR adds an `options` field to `BackendListVersionsCtx` and updates the other two backends so that their options field can store arbitrary TOML values.

## Issue 11

Pull request #8876: fix: skip trust check for plain .tool-versions in task list

## Summary

PR #8675 added trust gating for `.tool-versions` files containing Tera template syntax, but `task_list.rs` still calls `is_trusted()` on **all** config files when checking for untrusted configs. This causes plain `.tool-versions` files (just tool names and versions, no templates) to trigger trust errors like:

```
mise ERROR Config file(s) in ~/dev/myproject are not trusted: ~/dev/myproject/.tool-versions
Trust them with `mise trust`.
```

This skips the trust check for `.tool-versions` files that don't contain template syntax (`{{`, `{%`, `{#`), consistent with the parsing logic added in #8675.

## Changes

- `src/task/task_list.rs`: Added `is_plain_tool_versions()` helper that checks if a path is a `.tool-versions` file without Tera template markers. The `err_no_task` trust check now skips these files since they can't define tasks or execute code.

## Test plan

- [ ] Plain `.tool-versions` (e.g. `ruby 3.3.3\nnodejs 14.21.3`) no longer triggers trust error
- [ ] `.tool-versions` with template syntax (e.g. `nodejs {{ exec("echo 20") }}`) still requires trust
- [ ] `.mise.toml` trust behavior unchanged

## Issue 12

Pull request #8881: chore: release 2026.4.4

This is the release chore PR for version 2026.4.4. Prepare the release by regenerating the CHANGELOG.md entry for 2026.4.4 from the work merged in this span, following the repository's established git-cliff changelog conventions (grouped sections for features, bug fixes, refactor, documentation, testing, dependency updates, registry changes, chores, and new contributors).

The 2026.4.4 entry must summarize, in the repository's changelog style, the span's merged changes, including: the CI workflow that auto-converts external PRs to draft mode; the new user-specified tool dependency field; runtime-only .NET installs; applying install_before to transitive npm dependencies; passing arguments to task dependencies through usage templates; the new options field on the backend list-versions context; the PEP 440 dev-version filtering fix; the e2e Docker image build-dependency fixes; the env flag parsing fix; the seccomp syscall autofix hardening; the GitHub backend tool-option preservation fixes; the provenance verification setting at lock time; stale lockfile entry pruning; the precompiled Python lockfile URL fix; the release build-target verification; Ruby precompiled build revisions; the Swift Ubuntu fallback; the zsh duplicate trust warning fix; the direnv empty-diff fix; the plain .tool-versions trust check skip; the go settings namespace rename; the task_config.includes documentation clarification; the Dockerized e2e test change; the dependency bumps; the registry addition and removal; the vendored aqua-registry warning workflow; the draft-conversion token change; and the removal of deprecated settings older than twelve months. Attribute entries per the repository's changelog conventions using the repository history; do not invent attributions.

Also update the vendored aqua registry for this release: register the six newly added packages (oyo, jiq, dealve-tui, jsongrep, lazyjira, and vize) and refresh the cosign package definition, using the vendored registry's own file layout and format.
## Issue 13

Pull request #8882: fix(exec): use i64::from() for seccomp syscall numbers to survive autofix

## Summary
- The previous `as i64` fix for armv7 seccomp build was reverted by autofix-ci because clippy on x86_64 flags it as an unnecessary cast (SYS_* is already i64 there)
- Uses `i64::from(syscall)` instead, which clippy won't flag and handles both i32 (armv7) and i64 (x86_64/aarch64)

## Test plan
- [ ] Verify `build-tarball-linux-armv7` CI job passes
- [ ] Verify clippy/autofix doesn't revert the change


## Issue 14

Pull request #8884: registry: add turso (github:tursodatabase/turso-cli)

Adds `turso` to the built-in registry using `github:tursodatabase/turso-cli`.

Validated with:

```bash
./target/debug/mise test-tool turso
```

## Issue 15

Pull request #8886: fix(release): verify all build targets succeed before releasing

## Summary
- Adds a verification step to the `release` job that explicitly checks all upstream jobs (`build-tarball-linux`, `build-tarball-macos`, `build-tarball-windows`, `e2e-linux`, `rpm`, `deb`) returned `success`
- Prevents releases when matrix variants (e.g. armv7) fail — currently the `!cancelled() && !failure()` condition treats skipped downstream jobs as passing, allowing the release to proceed

## Context
PR #8881 (release 2026.4.4) is currently mergeable despite `build-tarball-linux-armv7` and `build-tarball-linux-armv7-musl` failing. The armv7 failures cause `e2e-linux`, `rpm`, and `deb` to be skipped, but `!failure()` doesn't consider skipped jobs as failures.

## Test plan
- [ ] Verify the release workflow still succeeds when all targets build correctly
- [ ] Verify the release job fails early if any build target fails (e.g. armv7)


## Issue 16

Pull request #8887: fix(docs): use sans-serif font for badges

## Summary
- Badge component was inheriting the serif heading font (Cormorant Garamond) instead of the base sans-serif font (Roc Grotesk)
- Added explicit `font-family: var(--vp-font-family-base)` to the `.badge` class

## Test plan
- [ ] Verify experimental/warning badges render in Roc Grotesk on docs pages (e.g., sandboxing, secrets)


## Issue 17

Pull request #8888: fix(github): preserve tool options like filter_bins when version specified via CLI

## Summary
- When a tool version is provided as a CLI argument (e.g. `mise bin-paths tool@version`), the `ToolsetBuilder` was creating a new `ToolRequest` without options, then destructively merging it over the config entry — losing `filter_bins` and other tool options.
- Now carries over options from the existing config when the CLI arg doesn't specify its own.

Closes #8885

## Test plan
- [x] Added e2e assertion to `test_github_filter_bins` verifying `mise bin-paths github:jgm/pandoc@3.8.2` returns the `.mise-bins` path
- [x] `cargo check` passes
- [x] All pre-commit lints pass


## Issue 18

Pull request #8889: fix(env): parse --env=VALUE and -E=VALUE flag forms correctly

## Summary
- Fix `--env=production` and `-E=production` (equals-sign form) being silently ignored, causing fallback to the default environment from `.miserc.toml`
- The `environment()` function in `src/env.rs` parsed args using `windows(2)` which only matched space-separated flag/value pairs (`--env production`), not the `=`-joined form
- Now handles both `--env production` and `--env=production` (and likewise `-E`, `-P`, `--profile`)

Fixes #8883

## Test plan
- [ ] `mise --env=production env` produces same output as `mise --env production env`
- [ ] `mise -E=production env` produces same output as `mise -E production env`
- [ ] `mise --env production env` still works as before
- [ ] `mise -E production env` still works as before
- [ ] Comma-separated values work: `mise --env=dev,staging env`


## Issue 19

Pull request #8892: fix(github): use alias-specific options when tool_alias has its own config

## Summary
- Fixed regression where `tool_alias` with per-alias `asset_pattern` (or other options) would use the original tool's options instead of the alias-specific ones
- Changed `get_tool_opts()` to prefer the alias-specific config entry when it has options set, falling back to the resolved name match for CLI-created requests without options (preserves the treesize/gitlab fix from #8084)
- Added e2e test verifying both the original tool and its alias install with their respective asset patterns

Fixes https://github.com/jdx/mise/discussions/8847

## Test plan
- [x] `cargo test` — all 563 unit tests pass
- [x] `mise run test:e2e test_github_tool_alias_asset_pattern` — new e2e test passes
- [x] All lint hooks pass


## Issue 20

Pull request #8893: feat(task): allow passing arguments to task dependencies via {{usage.*}} templates

## Summary
- Task dependencies can now reference parent task arguments using `{{usage.*}}` templates in `depends`, `depends_post`, and `wait_for`
- Arguments flow through dependency chains (A -> B -> C) — each task parses its own usage spec and re-renders child dependency templates with resolved values
- Works with both positional args (`arg`) and flags (`flag`), and with both string and structured dependency syntax

### Example

```toml
[tasks.build]
usage = 'arg "<app>"'
run = 'echo "building {{usage.app}}"'

[tasks.deploy]
usage = 'arg "<app>"'
depends = [ { task = "build", args = ["{{usage.app}}"] } ]
run = 'echo "deploying {{usage.app}}"'
```

```
$ mise run deploy myapp
[build] building myapp
[deploy] deploying myapp
```

Closes discussion #4331

## Implementation

Dependency templates containing `{{usage.*}}` are deferred during initial config loading (since CLI args aren't available yet). They are re-rendered later with actual usage values at two points:

1. **Top-level tasks** — after CLI args are resolved in `run.rs`, before dependency graph construction
2. **Dependency chain tasks** — during `Deps::new()` graph building, when a task receives args from its parent

Key changes:
- `Task` stores raw (unrendered) dependency templates in `depends_raw`/`depends_post_raw`/`wait_for_raw`
- New `render_depends_with_usage()` method re-renders deps with a `usage` context
- New `parse_usage_values_from_task()` parses a task's usage spec against its args to extract named values
- Dependency resolution (`resolve_depends`, `all_depends`) skips deps with unresolved `{{usage.*}}` refs

## Test plan
- [x] E2E test `test_task_dep_args` covering:
  - Basic arg passing to dependency
  - Flag passing to dependency
  - Multiple parallel dependencies receiving the same arg
  - String syntax (`depends = ["child {{usage.name}}"]`)
  - Dependency chaining (A -> B -> C, args flow through all levels)
- [x] All existing dep-related e2e tests pass (dep_env, deps, run_depends, depends_post, depends_post_multiple, deps_circular, skip_deps, failure_hang_depends, delegation_dedup, double_dash_behavior, args_position)
- [x] All 563 unit tests pass


## Issue 21

Pull request #8894: registry: remove carp test

## Summary
- Remove the test for `carp` registry entry since `carp-lang/Carp` latest release (v0.6.0) has no binary assets for any platform, causing CI failures in `test-tool-retry`

## Test plan
- [x] Lint checks pass locally
- [ ] CI `test-tool-retry` no longer fails on carp


## Issue 22

Pull request #8896: feat(ci): auto-convert external PRs to draft mode

## Summary
- Adds a GHA workflow that auto-converts PRs from external contributors to draft mode
- Leaves a comment telling the author to mark it ready when they want human review
- Skips PRs from jdx and renovate[bot]

## Test plan
- [ ] Open a test PR from a non-owner account and verify it gets converted to draft with the comment


## Issue 23

Pull request #8897: chore(ci): add workflow to warn PRs modifying vendored aqua-registry

## Summary
- Adds a GitHub Actions workflow that automatically comments on PRs that modify files under `crates/aqua-registry/aqua-registry/pkgs/`
- Directs contributors to submit package definitions to the upstream [aqua-registry](https://github.com/aquaproj/aqua-registry) instead
- Deduplicates comments so only one warning is posted per PR

## Test plan
- [ ] Open a test PR touching a file under `crates/aqua-registry/aqua-registry/pkgs/` and verify the comment is posted
- [ ] Verify no duplicate comments on subsequent pushes


## Issue 24

Pull request #8898: fix(zsh): avoid duplicate trust warning after cd

When entering an untrusted project in zsh, users currently see the same `mise trust` warning twice for a single `cd`.

The demo shows the duplicate warning, then patches the hooks in-shell and shows the warning appearing once.


This changes the zsh hook setup to use [`add-zsh-hook`](https://zsh.sourceforge.io/Doc/Release/User-Contributions.html#Manipulating-Hook-Functions), matching zsh’s documented model for managing [`precmd` and `chpwd`](https://zsh.sourceforge.io/Doc/Release/Functions.html#Hook-Functions) hooks.
  
 
![Duplicate zsh trust warning demo](https://github.com/user-attachments/assets/1b4a60af-ea18-4782-9df9-dbfe4b99606c)

## Issue 25

Pull request #8899: test(ci): run e2e tests inside Docker containers

## Summary
- Add `packaging/e2e/Dockerfile` (Ubuntu 26.04) with all e2e test dependencies (bash, zsh, fish, git, jq, direnv, fd-find, build-essential, python3, nushell, etc.)
- Add `e2e` to docker.yml build matrix so `ghcr.io/jdx/mise:e2e` is built and pushed to GitHub packages
- Modify `e2e/run_test` to optionally run tests inside Docker containers when `MISE_E2E_DOCKER=1` is set
- Add `docker-e2e` job to test.yml (opt-in via `workflow_dispatch` or `MISE_E2E_DOCKER_CI` repo variable)

## Usage
```bash
# Local (with locally built image)
docker build -t mise-e2e -f packaging/e2e/Dockerfile .
MISE_E2E_DOCKER=1 MISE_E2E_DOCKER_IMAGE=mise-e2e ./e2e/run_test cli/test_version

# Local (with pre-built image from GHCR)
MISE_E2E_DOCKER=1 ./e2e/run_test cli/test_version

# Run all tests in Docker
MISE_E2E_DOCKER=1 ./e2e/run_all_tests
```

## Test plan
- [x] Built Docker image locally and verified it builds successfully
- [x] Ran `cli/test_version` inside Docker container — passed
- [x] Ran `cli/test_alias` inside Docker container — passed (including tool install)
- [ ] Verify `ghcr.io/jdx/mise:e2e` image builds in docker.yml workflow
- [ ] Verify docker-e2e job runs when triggered via workflow_dispatch


## Issue 26

Pull request #8900: fix(ruby): support build revisions for precompiled binaries in mise.lock

## Summary
- When resolving precompiled Ruby binaries from `jdx/ruby`, prefer the latest build revision tag (e.g., `3.3.11-1` over `3.3.11`)
- Build revisions are tagged as `{version}-{N}` where N is an incrementing integer, representing rebuilds of the same upstream Ruby version
- Once a build revision is locked in `mise.lock`, subsequent `mise lock` runs preserve it instead of upgrading to a newer build revision
- This prevents `mise.lock` from breaking when binaries are rebuilt with different checksums

## Background
The `jdx/ruby` repo now publishes build revision tags (e.g., `3.3.11` and `3.3.11-1`). When binaries are rebuilt, the old release's checksums become stale. Previously, mise always fetched the exact version tag, so a lockfile created against `3.3.11` would break if the binaries were later republished as `3.3.11-1`.

## Changes
- **`src/github.rs`**: Added `get_release_with_build_revision()` + shared `pick_best_build_revision()` helper that finds the highest `{version}-N` tag from releases; unit tests exercise the shared helper directly
- **`src/plugins/core/ruby.rs`**: Added `extract_build_revision_from_lock_platforms()` to parse existing lockfile URLs for build revision tags; threads `locked_build_revision` through `find_precompiled_asset_in_repo` so locked revisions are preserved across `mise lock` runs, falling back to latest if the locked revision is deleted

## Test plan
- [x] Unit tests for build revision selection logic (4 tests: highest wins, fallback to base, no match, non-numeric suffixes ignored)
- [ ] Verify `mise use ruby@3.3.11` installs from the `-1` build revision release
- [ ] Verify `mise lock` captures the build revision URL in the lockfile
- [ ] Verify re-running `mise lock` preserves the existing build revision


## Issue 27

Pull request #8901: fix(install): add locked_verify_provenance setting and detect github attestations at lock time

## Summary

**Lock-time verification (current platform):**
- During `mise lock`, for the current platform, downloads the artifact to a temp directory and runs full cryptographic verification (GitHub attestations, SLSA, cosign, minisign) before recording provenance in the lockfile
- Cross-platform entries still use detection-only (registry metadata) since we can't easily verify artifacts for other platforms
- If verification fails, provenance is not recorded (warning logged)

**Install-time re-verification setting:**
- Adds `locked_verify_provenance` setting (`MISE_LOCKED_VERIFY_PROVENANCE`, default: false, auto-enabled under `MISE_PARANOID`) that forces provenance re-verification at install time even when the lockfile already has both checksum and provenance

**GitHub attestations at lock time:**
- Enables GitHub artifact attestations as highest-priority provenance detection in `detect_provenance_type()` (what #8781 intended)
- Applies the same `force_verify` logic to both `aqua` and `github` backends

**Security context:** Previously, `detect_provenance_type()` recorded provenance from aqua registry metadata without cryptographic verification, and `mise install --locked` skipped `verify_provenance()` entirely when the lockfile had both checksum and provenance. This meant provenance was never actually verified in the `mise lock` → `mise install` flow. Lock-time verification for the current platform closes this gap, and the `locked_verify_provenance` setting provides additional protection for paranoid users.

Supersedes #8781 — incorporates the GitHub attestations detection change while addressing the underlying security gap discussed there.

## Test plan

- [ ] Verify `cargo check` passes (confirmed locally)
- [ ] Verify `mise lock` records `github-attestations` provenance for tools with `github_artifact_attestations` in aqua registry (e.g., `jq >= 1.8.0`) after downloading and verifying the artifact
- [ ] Verify `mise lock` logs verification activity for current platform tools with provenance
- [ ] Verify `mise install --locked` skips provenance verification by default (existing behavior preserved)
- [ ] Verify `env MISE_LOCKED_VERIFY_PROVENANCE="1" mise install --locked` re-verifies provenance at install time
- [ ] Verify `MISE_PARANOID=1 mise install --locked` also re-verifies provenance
- [ ] Verify cross-platform lock entries still get provenance from metadata detection (no download)
- [ ] Verify the new setting appears in `mise settings ls` and schema


## Issue 28

Pull request #8903: chore(ci): use github.token for draft conversion in auto-draft workflow

## Summary

- Split the auto-draft step into two: draft conversion uses `github.token`, comment uses `MISE_PR_COMMENT_TOKEN`
- Fine-grained PATs don't support the `convertPullRequestToDraft` GraphQL mutation, causing the workflow to fail with `Resource not accessible by personal access token`
- `github.token` with `pull-requests: write` permission supports this mutation

Fixes the failure seen in https://github.com/jdx/mise/actions/runs/23982740067/job/69949629833

## Test plan

- [ ] Open a test PR from a non-collaborator fork to verify the workflow converts it to draft and posts the comment


## Issue 29

Pull request #8904: chore: remove deprecated settings older than 12 months

## Summary
- Remove 14 deprecated setting aliases that have had replacements for 18+ months (since Sep-Nov 2024)
- Settings removed: `asdf`, `cargo_binstall`, `disable_default_shorthands`, `npm.bun`, `pipx_uvx`, `python_compile`, `python_default_packages_file`, `python_patch_url`, `python_patches_directory`, `python_precompiled_arch`, `python_precompiled_os`, `python_pyenv_repo`, `python_venv_stdlib`, `vfox`
- Removes associated migration code in `settings.rs` and legacy e2e tests
- `asdf_compat` and `profile` are kept (still has active code usage / env var fallback)

## Test plan
- [x] `cargo build` compiles cleanly
- [x] `mise run lint` passes
- [x] Schema regenerated
- [ ] CI passes


## Issue 30

Pull request #8905: docs(tasks): clarify task_config.includes behavior

## Summary

Follow-up to #8740.

That PR proposed changing `task_config.includes` semantics, but the conclusion in the discussion was to document the current behavior instead of making a breaking change.

This updates the task docs to reflect how `task_config.includes` works today:

- explicit `task_config.includes` replaces the default file-task directories for that config scope
- if users want the defaults plus custom paths, they must list the defaults explicitly
- for local/monorepo task discovery, the nearest config with `task_config.includes` wins
- global config files are loaded independently, so each global config file uses its own `includes` or the defaults

It also updates the file-tasks page so the default directories are clearly described as defaults rather than always-on search paths.

## Verification

- `git diff --check`
- `mise run docs:build`

## Issue 31

Pull request #8906: chore(deps): bump ubi from 0.8 to 0.9

## Summary
- Bumps `ubi` from 0.8.4 to 0.9.0 (adds `min_age_days` feature, no breaking API changes)
- This pulls in `sevenz-rust2` 0.20.2 → `lzma-rust2` 0.16.2, which resolves the `crc` version conflict causing CI failures in #8416
- The root cause: `lzma-rust2` 0.15.x pins `crc =3.3` exactly, but `crc` 3.4.0 was published, causing Cargo to fall back to `lzma-rust2` 0.15.3 with `crc <=3.3` → resolved `crc` 2.1.0 → compile error

## Test plan
- [x] `cargo check` passes locally
- [x] All pre-commit lints pass
- [ ] CI passes


## Issue 32

Pull request #8908: chore(deps): bump zip from 3 to 8

## Summary
- Bumps direct `zip` dependency from 3.0.0 to 8.5.0
- Helps resolve the `lzma-rust2`/`crc` version conflict in #8416 by reducing the number of separate `zip` versions in the dependency tree

## Test plan
- [x] `cargo check` passes locally
- [x] All pre-commit lints pass
- [x] CI passes


## Issue 33

Pull request #8909: chore(deps): update lockfile deps (hold back rattler)

## Summary
- Updates all lockfile dependencies to latest compatible versions
- Holds back rattler crates due to `rattler_virtual_packages` 2.3.12+ requiring `rattler_conda_types` 0.44 while other rattler crates still pin 0.43.4
- Eliminates `zip` 7 and `lzma-rust2` 0.15.x from the dep tree, resolving the `crc` version conflict in #8416

## Test plan
- [x] `cargo check` passes locally
- [x] All pre-commit lints pass
- [x] CI passes


## Issue 34

Pull request #8910: fix(ci): add Ruby build dependencies to e2e Docker image

## Summary
- Add `libssl-dev`, `libreadline-dev`, `libyaml-dev`, `libffi-dev`, and `zlib1g-dev` to the e2e Docker image
- Fixes `test_gem_slow` failure where `ruby-build` failed compiling OpenSSL from source because system dev headers were missing

## Test plan
- [x] Reproduced failure on bamboo with current image (OpenSSL build fails)
- [x] Verified fix on bamboo: Ruby 4.0.2 compiles successfully with system libssl-dev


## Issue 35

Pull request #8911: fix(ci): update COPR BuildRequires rust version to match MSRV 1.88

## Summary
- Update `BuildRequires: rust >= 1.85` to `rust >= 1.88` in the COPR spec template to match the project's MSRV

## Test plan
- Verified RHEL 9, RHEL 10, and Ubuntu 26.04 all ship Rust >= 1.88


## Issue 36

Pull request #8912: fix(ci): add missing build dependencies to e2e Docker image

## Summary
- Add `autoconf`, `cargo`, `libncurses-dev` to e2e Docker image
- Fixes all 8 failing e2e jobs:
  - `test_cargo_compile_slow`, `test_cargo_binstall_slow`, `test_cargo_features_slow`, `test_cargo_compile_git_slow`: cargo not installed
  - `test_erlang_slow`: missing autoconf and libncurses-dev
  - `test_vfox_python_slow`, `test_node_slow`, `test_gem_slow`: already fixed by #8910

## Test plan
- [x] Reproduced all failures on bamboo
- [x] Verified Erlang 27.2 builds with autoconf + libncurses-dev
- [x] Verified Python 3.12.0, Node, Ruby all build with current deps
- [x] Docker image build triggered: https://github.com/jdx/mise/actions/runs/23987561675


## Issue 37

Pull request #8913: chore(deps): update bun.lock

## Summary
- Updates bun.lock to latest dependency versions

## Test plan
- [x] All pre-commit lints pass
- [ ] CI passes


## Issue 38

Pull request #8914: fix(ci): add missing build dependencies to e2e Docker image

## Summary
- Add `autoconf`, `cargo`, `libncurses-dev`, `pkg-config` to e2e Docker image
- Fixes all 8 failing e2e jobs:
  - `test_cargo_*_slow`: cargo not installed, pkg-config missing for openssl-sys
  - `test_erlang_slow`: missing autoconf and libncurses-dev
  - `test_vfox_python_slow`, `test_node_slow`, `test_gem_slow`: already fixed by #8910

## Test plan
- [x] Reproduced all failures on bamboo
- [x] Verified Erlang 27.2, Python 3.12.0, Node, Ruby all build with new deps
- [x] Docker image build triggered: https://github.com/jdx/mise/actions/runs/23987968955


## Issue 39

Pull request #8915: fix(ci): use Node 24 LTS for corepack e2e test

## Summary
- Node 25 removed corepack, causing `test_node_slow` to fail when `mise latest node` returns 25.x
- Pin to Node 24 (LTS) which still ships corepack for the corepack/yarn assertions

## Test plan
- [x] Verified on bamboo: Node 24 installs with corepack shims, `which yarn` works
- [x] Verified Node 25 does not have corepack (confirmed the root cause)


## Issue 40

Pull request #8916: fix(swift): fall back to Ubuntu 24.04 for unsupported Ubuntu versions

## Summary
- Swift only provides binaries for Ubuntu 20.04, 22.04, and 24.04
- On Ubuntu 26.04, the download URL 404s (`ubuntu26.04` is not a valid Swift platform)
- Map unsupported Ubuntu versions to 24.04 (latest supported), matching the existing pattern for Fedora and UBI

## Test plan
- [x] Verified `https://download.swift.org/.../ubuntu24.04.tar.gz` returns 200
- [x] Verified `https://download.swift.org/.../ubuntu26.04.tar.gz` redirects to 404


## Issue 41

Pull request #8917: fix(ci): add libxml2 and pkg-config to e2e Docker image

## Summary
- Add `pkg-config` for cargo crates that link system libraries (openssl-sys)
- Add `libxml2` for Swift SPM support (swift-package links against libxml2.so.2)

## Test plan
- [x] pkg-config: fixes `openssl-sys` build failure in cargo backend tests
- [x] libxml2: fixes `swift-package: error while loading shared libraries: libxml2.so.2` in test_swift_slow
- [x] Docker image build triggered: https://github.com/jdx/mise/actions/runs/23989620731


## Issue 42

Pull request #8918: fix(ci): add libxml2-dev to e2e image and disable Swift SPM tests

## Summary
- Add `libxml2-dev` to e2e Docker image
- Disable SPM tests in `test_swift_slow`: Swift 24.04 binaries link against `libxml2.so.2` but Ubuntu 26.04 ships `libxml2.so.16` (ABI mismatch). SPM tests will fail until Swift provides native 26.04 binaries.

## Test plan
- [x] Confirmed ABI mismatch: Swift's `swift-package` expects `libxml2.so.2`, Ubuntu 26.04 has `libxml2.so.16`
- [x] Swift install + `swift --version` still works (only SPM is broken)


## Paths the verifier owns

The grader applies its own version of the 44 path(s) below. Leave every one of them exactly as
it is, including any file a tool of yours would rewrite as a side effect: a submission that changes
one is rejected before a single test runs, and the whole session scores zero however good the rest
of it is. The issue text above asks for changes in 7 of them; that ask does not apply.

- `e2e-win/npm_backend.Tests.ps1`
- `e2e/backend/test_aqua_cosign`
- `e2e/backend/test_backend_missing_deps`
- `e2e/backend/test_dev_version_filter`
- `e2e/backend/test_github_filter_bins`
- `e2e/backend/test_github_tool_alias_asset_pattern`
- `e2e/backend/test_npm_package_manager`
- `e2e/cli/test_env_flag_forms`
- `e2e/cli/test_tool_depends`
- `e2e/cli/test_watch`
- `e2e/cli/test_zsh_precmd_runs_once`
- `e2e/config/test_config_ignore`
- `e2e/core/test_dotnet`
- `e2e/core/test_node_slow`
- `e2e/core/test_rust`
- `e2e/core/test_swift_slow`
- `e2e/env/test_fish_path_move_bug`
- `e2e/env/test_zsh_consecutive_precmd_runs`
- `e2e/env/test_zsh_first_precmd_after_activate`
- `e2e/generate/test_generate_bootstrap`
- `e2e/helpers.sh`
- `e2e/lockfile/test_lockfile_lock_filtered_prune_stale_versions`
- `e2e/lockfile/test_lockfile_lock_unfiltered_prune_stale_versions`
- `e2e/lockfile/test_lockfile_provenance`
- `e2e/lockfile/test_lockfile_python`
- `e2e/plugins/test_plugin_link`
- `e2e/run_all_tests`
- `e2e/run_test`
- `e2e/tasks/test_task_dep_args`
- `e2e/tasks/test_task_monorepo_file_tasks`
- `e2e/tasks/test_task_remote_git_https`
- `e2e/tasks/test_task_remote_git_includes`
- `e2e/tasks/test_task_remote_git_ssh`
- `e2e/tasks/test_tool_versions_trust`
- `packaging/e2e/Dockerfile`
- `src/config/config_file/snapshots/mise__config__config_file__mise_toml__tests__env_var_in_tool.snap`
- `src/config/config_file/snapshots/mise__config__config_file__mise_toml__tests__fixture-3.snap`
- `src/config/config_file/snapshots/mise__config__config_file__mise_toml__tests__replace_versions.snap`
- `src/shell/snapshots/mise__shell__zsh__tests__activate.snap`
- `src/shell/snapshots/mise__shell__zsh__tests__deactivate.snap`
- `test/data/plugins/needs-dummy/bin/download`
- `test/data/plugins/needs-dummy/bin/install`
- `test/data/plugins/needs-dummy/bin/latest-stable`
- `test/data/plugins/needs-dummy/bin/list-all`

Everything else the issues ask for still applies, including changes to non-test code these paths
exercise. If a command of yours regenerates one of them, restore it before you finish.
## Working instructions

The issue sections above usually describe MANY separate issues, not one. Your job is to implement the changes required by EVERY issue they contain — not just the one that looks most tractable, most self-contained, or easiest to identify. There is no single "real" issue hidden among the others; treat all of them as in scope.

The tests that grade this task are hidden: the updated test files are applied only when your work is graded. The tests you can see in the repository may be outdated and may contradict the issues above, so when a visible test disagrees with an issue, follow the issue text, not the visible test. You MUST NOT modify the testing logic or any of the tests in any way. This prohibition covers not only `_test` files but also test helper packages, fixtures, fakes, stubs, mocks, and example or integration applications that exist to support tests under the test paths described next. If a visible test fails because it asserts behaviour an issue asks you to change, leave the test as it is and implement what the issue asks.

The prohibition is by path, not by file type. Do not write to anything inside a test directory — for example `tests/`, `test/`, `e2e/`, `testdata/`, or any path nested beneath one — even when the file is a README, a markdown document, a diagram, or a config that plainly cannot affect a test result. A submission that touches any path under the graded test tree is rejected in full and scores nothing, however correct the rest of the work is. If an issue on your checklist asks for a change under such a path, mark it BLOCKED with that reason and move to the next issue.

Leave repository plumbing alone on the same terms unless an issue names the file directly: CI workflow definitions, issue and pull-request templates, Helm charts, container manifests, and dependency lockfiles. Treat dependency manifests such as requirements files, package.json, or go.mod as plumbing too, except that a change an issue explicitly asks for, such as a version bump, is in scope, and if that change cannot be built without downloading anything, mark the issue BLOCKED with that reason.

The development environment is already set up for you (i.e., all dependencies are already installed). Do not download or install any package or dependency, including a different, newer, or "fixed" version of the package(s) under test, and do not fetch any external source, release, or patch to obtain the solution.

Your task is to make thorough, complete changes to non-test files in the repository that address EVERY issue above. Do not optimise for a small diff — breadth of coverage across all the issues matters more than the size of any individual change. At the same time, scope each edit to what its issue actually calls for; do not refactor unrelated code for style.

Solve this using only the code already present in the repository; do not retrieve the reference solution from any external source (do not clone, fetch, or pull the upstream repository or a mirror; do not download or install a different, newer, or "fixed" version of the package(s) under test; do not fetch pull-request or commit diffs; and do not read post-baseline git history, tags, stashes, or remotes to locate the change). A solution derived from a retrieved reference is invalid and will not be scored.

Step 0 — Enumerate before you edit.
Read the issues above from beginning to end and write out a numbered checklist of every distinct issue they describe (one entry per `## Issue N` header). State the total explicitly, for example: "Checklist: 34 issues found." Do not begin editing until this checklist exists. Do not attempt to guess which issue is "the important one" — you cannot tell, and guessing is the single most common way this task is failed.

Then work the checklist in order. For each issue, announce which one you are on ("Working on issue N of M: <short title>") and carry out the following:

1. Explore the repo to locate the code responsible for this issue. On the first issue, take extra time to familiarise yourself with the overall structure.
2. Create a script to reproduce the behavior described and execute it using the appropriate command for the repository's language, to confirm it.
3. Edit the source code of the repo to make the change this issue calls for.
4. Rerun your reproduction and check the behavior.
5. Build or compile every package you touched and confirm it compiles cleanly. A change that does not compile scores nothing, and it can break packages that were passing before you started. If you change a function signature, an interface, or a type, find and update every caller and every implementer of it in non-test code before moving on; visible test files that still use the old form are the exception, since you may not edit them.
6. Think about edge cases, add checks for them in your reproduction script, and run them to see how your change handles them.
7. Mark this issue DONE on your checklist, then move to the next one. If an issue genuinely cannot be worked — because it is a pre-existing environment failure unrelated to your changes, or it would require retrieving external code — mark it BLOCKED, state the specific reason in one sentence, and move to the next issue. A blocked issue never ends the session; it only ends work on that issue.

Do not stop early, and do not end the session without calling the `finish` tool: work that is never submitted with `finish` is discarded unscored. Finishing after addressing only one issue, or only a handful, is the primary failure mode on this task — work every item on the checklist, not just the first tractable one. Do not pad with busywork either: every step should be locating, editing, building, or testing real code for a real checklist item. Do not call the `finish` tool until every item on your checklist is marked either DONE or BLOCKED with a stated reason and you have completed the review pass described below. When you finish, report the final tally: how many issues you addressed, and which ones you marked BLOCKED and why.

Once you have made a first pass over the whole checklist, carefully re-read the issues above and review your own changes with `git diff`. For each issue, check whether the change you made matches what it asked for. Write scratch checks outside every test directory and every `_test` file to probe the correctness of your changes, specifically focusing on checks that may point out remaining gaps. Run the tests in the repo related to what you changed and check whether any fail — pay particular attention to tests that were passing before your changes and are failing now, since breaking working code costs more than leaving an issue unaddressed, unless the failing test asserts behaviour an issue asks you to change. Repeat this process of re-reading, testing, and adjusting until you have attempted every checklist item and the packages you touched build cleanly. Find and run any tests in the repo that are related to:
   - Each issue on your checklist
   - The files you modified
   - The functions you changed

Your thinking should be thorough and so it's fine if it's very long. Think carefully before each edit about which issue it serves and what else it might break.

When the review pass is complete and every checklist item is marked DONE or BLOCKED, call the `finish` tool to end the session.

Calling `finish` is what submits your work. The session is scored only if you call it: a session that stops without calling `finish` is discarded, and every change you made scores nothing, however complete it was. Running out of things to say is not finishing. When the checklist is done, call `finish` as your last action, and if you are ever unsure whether you have more to do, call `finish` rather than stopping silently.
