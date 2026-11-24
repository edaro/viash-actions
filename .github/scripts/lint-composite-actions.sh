#!/usr/bin/env bash
# Lint the `run:` blocks of all composite actions in this repository.
#
# actionlint only checks workflow files, so the scripts embedded in the
# composite actions' `action.yml` files are checked here instead:
#
#  * every `run:` block must have `shell: bash`;
#  * no `run:` block may contain a `${{ ... }}` expression (pass values via
#    `env:` instead, to avoid script injection);
#  * every `run:` block must pass shellcheck.
#
# Usage: .github/scripts/lint-composite-actions.sh [shellcheck args...]
# Requires: git, yq (mikefarah), shellcheck.

set -euo pipefail

repo_root=$(git rev-parse --show-toplevel)
cd "$repo_root"

tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

failed=0

while IFS= read -r action_file; do
  if [ "$(yq '.runs.using' "$action_file")" != "composite" ]; then
    continue
  fi

  num_steps=$(yq '.runs.steps | length' "$action_file")
  for ((i = 0; i < num_steps; i++)); do
    has_run=$(yq ".runs.steps[$i] | has(\"run\")" "$action_file")
    if [ "$has_run" != "true" ]; then
      continue
    fi

    step_name=$(yq ".runs.steps[$i].name // .runs.steps[$i].id // \"step $i\"" "$action_file")
    label="$action_file: '$step_name'"

    shell=$(yq ".runs.steps[$i].shell // \"\"" "$action_file")
    if [ "$shell" != "bash" ]; then
      echo "::error file=$action_file::$label: expected 'shell: bash', got '$shell'"
      failed=1
      continue
    fi

    script_file="$tmp_dir/script.sh"
    {
      echo "#!/usr/bin/env bash"
      yq ".runs.steps[$i].run" "$action_file"
    } > "$script_file"

    # shellcheck disable=SC2016 # the literal string '${{' is intended
    if grep -nF '${{' "$script_file" > "$tmp_dir/expressions.txt"; then
      echo "::error file=$action_file::$label: \${{ }} expressions in 'run:' are not allowed, pass them via 'env:' instead"
      sed 's/^/    /' "$tmp_dir/expressions.txt"
      failed=1
    fi

    if ! shellcheck --shell=bash "$@" "$script_file" > "$tmp_dir/shellcheck.txt"; then
      echo "::error file=$action_file::$label: shellcheck failed"
      sed "s#$script_file#<run>#g" "$tmp_dir/shellcheck.txt"
      failed=1
    fi
  done
done < <(git ls-files '*action.yml' ':!:**/node_modules/**')

if [ "$failed" -ne 0 ]; then
  exit 1
fi
echo "All composite action scripts passed."
