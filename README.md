# Github Actions for Viash


This repository stores Github Actions useful for building and publishing
[Viash](https://viash.io) components:

1.  [`ns-build`](ns-build) - viash ns build
2.  [`ns-list`](ns-list) - viash ns list
3.  [`setup`](setup) - Setup Viash

There are also some actions that are commonly used in Viash projects:

1.  [`project/build-target`](project/build-target) - Build target
    directory
2.  [`project/check-concurrent-pr`](project/check-concurrent-pr) - Check
    for concurrent PRs
3.  [`project/detect-changed-components`](project/detect-changed-components) -
    Detect components with changed files
4.  [`project/sync-and-cache-s3`](project/sync-and-cache-s3) - Sync and
    cache an S3 bucket
5.  [`project/sync-and-cache`](project/sync-and-cache) - Sync and cache
    test resources specified by the project config
6.  [`project/update-docker-engine`](project/update-docker-engine) -
    Update Docker Engine

Finally, there are some [Viash
Pro](https://www.data-intuitive.com/services/viashpro.html) actions:

1.  [`pro/build-nextflow-params`](pro/build-nextflow-params) - Build
    parameter yaml examples for Viash components
2.  [`pro/build-nextflow-schemas`](pro/build-nextflow-schemas) - Build
    nf-tower schemas for Viash components
3.  [`pro/generate-documentation-qmd`](pro/generate-documentation-qmd) -
    Build quarto markdown documentation files for Viash components

We recommend using `v7` for your actions.

## Release Management

This repository uses [GitHub’s recommended release management for
actions](https://docs.github.com/en/actions/creating-actions/about-custom-actions#using-release-management-for-actions):

- GitHub releases with tags are used for updates on the actions.
- Semantic versioning is used, with major, minor and possibly patch
  release.
- Major versions (such as `v1`) will always point to the last minor or
  patch release for this major version. (when `v1.0.2` is out, `v1` will
  point to this update to). This means using
  `edaro/viash-actions/setup@v1` in your workflow file will
  automatically get the updated versions. Using
  `edaro/viash-actions/setup@v1.0.2` will pin a specific release.
- Major version changes (`v1` to `v2`) will often come with breaking
  changes, and workflows might require manual updates.
