#!/usr/bin/env bash
set -uo pipefail

cd "$(git rev-parse --show-toplevel)"

if ! git diff --quiet; then
    echo "Stage your change first: the files the hooks rewrite are staged for you." >&2
    exit 1
fi

venv=backend/.venv
[[ -d $venv ]] || venv="$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")/backend/.venv"
VIRTUAL_ENV="$(cd "$venv" && pwd)" || exit 1
export VIRTUAL_ENV PATH="$VIRTUAL_ENV/bin:$PATH" PYTHONPATH="$PWD/backend" OTEL_SDK_DISABLED=true

untracked() { git ls-files --others --exclude-standard; }
before="$(untracked)"

for _ in 1 2 3 4 5; do
    pre-commit run "$@" && exit 0
    added="$(comm -13 <(echo "$before") <(untracked))"
    if git diff --quiet && [[ -z $added ]]; then
        exit 1
    fi
    git add -u
    while read -r file; do
        [[ -n $file ]] && git add -- "$file"
    done <<<"$added"
done
exit 1
