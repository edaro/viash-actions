#!/usr/bin/env bash
# Check the test resources synced by project/sync-and-cache for a fixture project.
#
# Usage: .github/scripts/check-fixture.sh <project_directory>
#
# The project directory must contain an `expected.md5` file (output of `md5sum`,
# paths relative to the project directory). This script checks that:
#
#  * every file listed in `expected.md5` exists and has the expected checksum;
#  * the `dest` paths of the test resources in `_viash.yaml` contain no other files.

set -euo pipefail

project_dir="$1"
cd "$project_dir"

echo "Checking checksums in '$project_dir/expected.md5'"
md5sum --check --strict expected.md5

expected=$(awk '{ print $2 }' expected.md5 | sort -u)
actual=$(
  yq e '.info.test_resources[].dest' _viash.yaml | while IFS= read -r dest; do
    if [ -d "$dest" ]; then
      find "$dest" -type f
    elif [ -e "$dest" ]; then
      echo "$dest"
    fi
  done | sort -u
)

if [ "$expected" != "$actual" ]; then
  echo "The files under the test resource destinations do not match 'expected.md5':"
  diff <(echo "$expected") <(echo "$actual") || true
  exit 1
fi
echo "All test resources are present and nothing else was found."
