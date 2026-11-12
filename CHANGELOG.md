# viash-actions unreleased

## Breaking changes

* All actions and reusable workflows now refer to `edaro/viash-actions/...@v7` instead of `viash-io/viash-actions/...@v6` (PR edaro/viash-actions#1).

* `ns-build`, `ns-list`: Run on Node 24 instead of the deprecated Node 20 (PR edaro/viash-actions#1).

* Bump third-party actions to their latest major versions, which run on Node 24 (PR edaro/viash-actions#1):
  - `actions/checkout@v7`
  - `actions/cache@v6`, `actions/cache/restore@v6`
  - `tj-actions/changed-files` v47.0.6, `docker/login-action` v4.8.0, `peaceiris/actions-gh-pages` v4.1.0 and `data-intuitive/reclaim-the-bytes` v2, pinned by commit SHA.

## New functionality

* `project/sync-and-cache`: Add a `cache_hit` output (PR edaro/viash-actions#1).

* `project/sync-and-cache`: Add support for LaminDB artifacts and collections as test resources, e.g. `path: lamin://<owner>/<instance>/collection/<uid>` (PR edaro/viash-actions#2).

* `.github/workflows/test.yaml`: Add an optional `LAMIN_API_KEY` secret for test resources stored in a private LaminDB instance (PR edaro/viash-actions#2).

## Minor changes

* All actions and reusable workflows: Pass expressions to `run:` scripts via `env:` instead of interpolating `${{ ... }}` directly, to prevent script injection (PR edaro/viash-actions#1).

* `.github/workflows/build.yaml`, `.github/workflows/test.yaml`: Add a minimal `permissions:` block (PR edaro/viash-actions#1).

* `project/sync-and-cache-s3`: Emit the deprecation message as a GitHub warning annotation (PR edaro/viash-actions#1).

* Add CI for this repository: `actionlint` for the workflows, `shellcheck` for the scripts in the composite actions, and a workflow that tests `project/sync-and-cache` against fixture projects (PR edaro/viash-actions#1).

## Bug fixes

* `project/sync-and-cache`: Add `--delete` flag to sync commands so files removed from the remote source are also removed locally (PR #56).

* `project/check-concurrent-pr`: Detect the default branch correctly; `$GITHUB_DEFAULT_BRANCH` is not set by GitHub Actions (PR edaro/viash-actions#1).

* `project/detect-changed-components`: Quote array expansions so that file paths with spaces are matched correctly (PR edaro/viash-actions#1).

* `pro/build-nextflow-params`, `pro/build-nextflow-schemas`, `pro/generate-documentation-qmd`: Use `viash_pro_token` to look up the latest `viash_tools` release; the non-existent input `token` was used before (PR edaro/viash-actions#1).

* `pro/build-nextflow-schemas`: Generate one schema per component again; only the first component's output path was passed to the generator (PR edaro/viash-actions#1).

* `pro/generate-documentation-qmd`: Validate the `write_index` input correctly (PR edaro/viash-actions#1).

* `project/update-docker-engine`: Fix quoting of the apt source line (PR edaro/viash-actions#1).

* Fix the action paths in the README examples, e.g. `project/sync-and-cache` instead of `sync-and-cache` (PR edaro/viash-actions#1).

# viash-actions v6.7.3

## Minor changes

* `setup`: Simplify Viash setup to avoid timeouts (PR #47).

# viash-actions v6.7.2

## Minor changes

* `project/sync-and-cache`: Fix google storage sync (PR #46).

# viash-actions v6.7.1

## Minor changes

* `project/sync-and-cache`: Rerender readme (PR #45).

* `pro/generate-documentation-qmd`: Remove deprecated argument (PR #45).

# viash-actions v6.7.0

## New functionality

* `project/sync-and-cache`: Add support for gs buckets. Infer type from path if not provided (PR #44).

## Minor changes

* `project/sync-and-cache-s3`: Added deprecation warning in favor of `project/sync-and-cache` (PR #44).

# viash-actions v6.6.1

## Bug fixes

* `project/sync-and-cache`: Fix incorrect sha calculation for caching (PR #43).

# viash-actions v6.6.0

## New functionality

* Many actions: Add input `project_directory` to allow specifying the project directory (PR #42):
  - `ns-build`
  - `ns-list`
  - `project/build-target`
  - `project/detect-changed-components`
  - `project/sync-and-cache`

## Bug fixes

* `project/build-target`: Do not throw an error if there is no `.gitignore` in place (PR #42).

* `ns-build`, `ns-list`: If Viash throws an error, make sure that the error message gets printed (PR #42).

* `project/detect-changed-components`: Fix the action not listening to 'ci force' in commit messages (PR #42).

# viash-actions v6.5.0

## New functionality

* `build-nextflow-params` and `build-nextflow-schemas`: allow using viash versions starting from `0.9.0` (PR #41).

# viash-actions v6.4.0

## New functionality

* `.github/workflows/build.yaml`: Added a callable workflow for building Viash components (PR #38).

* `.github/workflows/test.yaml`: Added a callable workflow for testing Viash components (PR #38).

## Minor changes

* `project/detect-changed-components`: Simplify separator handling of changed files array (PR #40).

## Bug fixes

* `project/detect-changed-components`: Fix realpath not being able to resolve changed files (PR #39).


# viash-actions v6.3.1

## Bug fixes

* `project/sync-and-cache`: Skip caching steps in action if no test resources are found (PR #37).

# viash-actions v6.3.0

## New functionality

* `pro/generate_documentation_qmd`: add `--clean` parameter (PR #36).

# viash-actions v6.2.0

## New functionality

* `pro/generate_documentation_qmd`: add `--query` parameter (PR #35).

# viash-actions v6.1.0

## New functionality

* `project/sync-and-cache`: Added an action for syncing and caching test resources (PR #31).

## Minor changes

* `project/detect-changed-components`: Make action less verbose by not printing out every changed file for every component (PR #32).

* `ns-list`: Output the `main_script_type` of each component (PR #33).

* `project/detect-changed-components`: Output the `full_name` and `main_script_type` of each component (PR #33).

* Update documentation for various components (PR #34).

## Bug fixes

* `check-concurrent-pr`: Added input parameter `github_token` for checking concurrent PRs (PR #31).


# viash-actions v6.0.0

## Breaking changes

* `update-docker-engine` was moved to `project/update-docker-engine` (PR #27).

* `pro/build-nextflow-params`: Arguments `components` and `workflows` were removed in favour for the `target_dir` argument (PR #27).

* `pro/build-nextflow-schemas`: Arguments `components` and `workflows` were removed in favour for the `target_dir` argument (PR #27).

* Removed `viash-hub/deploy`: Viash Hub pulls source code from GitHub and builds Viash packages accordingly, as opposed to pushing deployments using GitHub Actions (PR #27).

## New functionality

* `project/build-target`: Created an action for building a target directory using `viash ns build` and generating a matrix of the components for which Docker images need to be built and pushed (PR #27).

* `project/check-concurrent-pr`: Created an action for checking if a push event is concurrent with a pull request (PR #27).

## Major changes

* All actions were updated to work with Viash 0.9 and later (PR #27).

## Documentation

* Updated all READMEs to be more consistent (PR #27).

* Added a Makefile for generating READMEs more efficiently (PR #27).


# viash-actions v5.3.1

## Bug fixes

* `project/detect-changed-components`: Fix components being listed more than once (PR #29).

# viash-actions v5.3.0

## New functionality

* `project/detect-changed-components`: Detect changed components when a resource is a directory (PR #28).

# viash-actions v5.2.1

## Bug Fixes

* `project/detect-changed-components`: fix changed components not being detected after updating `tj-actions/changed-files` (PR #25).

# viash-actions v5.2.0

## Minor changes

* `project/detect-changed-components`: bump `tj-actions/changed-files` to `42.0.2` (PR #24).

# viash-actions v5.1.0

## New functionality

* `pro/build-nextflow-schemas`: Add optional flag to allow dataset input for nf-tower (PR #23).

# viash-actions v5.0.0

## Breaking changes

* `ns-build` and `ns-list`: update to node20 (PR #20).

## Minor changes

* Update `actions/checkout@v3` to `actions/checkout@v4` and `actions/cache@v3` to `actions/cache@v4` (PR #20).

* Update several node dependencies (PR #20).

# viash-actions v4.1.1

## Minor changes

* `viash-hub/deploy`: Add a `commit_message` input parameter to allow specifying the commit message for the deployment.

* `viash-hub/deploy`: Fix dash in `src-branch` and `dest-branch` to underscore, now `src_branch` and `dest_branch`. Like any other parameter.

# viash-actions v4.1.0

## Minor changes

* `ns-build`, `ns-list`: Allow `config_mod` to be used as multiline text. Each line will become a separate `--config_mod` parameter.

## New functionality

* `viash-hub/deploy`: Add an action to deploy build artifacts from GitHub to Viash-Hub.

# viash-actions v4.0.0

## Breaking changes

* `pro/generate-documentation-qmd`: Renamed `working_directory` to `project_directory`, and renamed `input_dir` to `src` (#17).

# viash-actions v3.2.1

## Bug fixes

* `setup`: Add fallback to downloading the Viash installer (#18).

# viash-actions v3.2.0

## New features

* Added `update-docker-engine` (#15).

# viash-actions v3.1.2

## Bug fixes

`setup`: Fetch Viash from `dl.viash.io` instead of deprecated `get.viash.io`.

# viash-actions v3.1.1

## Bug fixes

`pro/generate-documentation-qmd`: Avoid building .qmd files for the components in the `viash_tools` repository by cloning it into `RUNNER_TEMP`.

# viash-actions v3.1.0

## New features

* `pro/generate-documentation-qmd`: Added `working_directory` option. 

## Bug fixes

* `project/detect-changed-components`: Refactor component resource detection.

# viash-actions v3.0.0

## New features

* Added `project/sync-and-cache-s3`: Sync and cache an S3 bucket.

* Added `project/detect-changed-components`: Filter a json produced by `ns-list` such that
  only components whose resources have changed in comparison to the default branch
  are retained.

## Minor changes

* `ns-list`: No longer prints output to interactive console.

## Breaking changes

* `pro/build-nextflow-params`:
  - Renamed from `build-nextflow-params`.
  - Input `token` was renamed to `viash_pro_token`.

* `pro/build-nextflow-schemas`:
  - Renamed from `build-nextflow-schemas`.
  - Input `token` was renamed to `viash_pro_token`.

* `pro/generate-documentation-qmd`:
  - Renamed from `generate-documentation-qmd`.
  - Input `token` was renamed to `viash_pro_token`.

# viash-actions v2.0.0

## New features

* Added `ns-build` - Build a namespace from many viash config files.

* Added `build-nextflow-schemas` - Build schemas from a viash config to use with nf-tower

* Added `build-nextflow-params` - build nextflow parameter file templates (see nextflow's -params-file option) from viash configs

## Major changes

* `ns-list`: Added arguments `query_namespace`, `query_name`, `platform`,
  `config_mod`, `format` and `parse_argument_groups` to make the action more in line with the
  arguments of `viash ns list`.

* `ns-list`: Added the `output_file` argument that allows writing the output for this action to a file.

* `setup`: Remove parameters that should be specified in `_viash.yaml`.

## Breaking changes

* `ns-list`: Renamed the output variable from `components_json` to simply `output`.
  The default format is `format: yaml`, set to `format: json` to restore the previous
  behaviour.

# viash-actions v1.0.0

Initial release. Contains the following actions:

* `setup`: Install Viash
* `ns-list`: List components in repo
