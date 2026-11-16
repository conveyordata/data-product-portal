#!/usr/bin/env bash
set -uo pipefail

cd "$(git rev-parse --show-toplevel)"

if [[ ${1-} == --files ]]; then
    check_only=1
elif ! git diff --quiet; then
    echo "Stage your change first: the files the hooks rewrite are staged for you." >&2
    exit 1
fi

candidates() {
    for dir in "$PWD/backend" "$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")/backend"; do
        [[ -d $dir/.venv ]] && echo "$dir/.venv"
        (cd "$dir" && poetry env list --full-path 2>/dev/null | cut -d' ' -f1)
    done
}
VIRTUAL_ENV=""
while read -r env; do
    if [[ -n $env ]] && (cd backend && VIRTUAL_ENV=$env poetry run true) >/dev/null 2>&1; then
        VIRTUAL_ENV=$env
        break
    fi
done < <(candidates)
if [[ -z $VIRTUAL_ENV ]]; then
    echo "No backend environment matches backend/pyproject.toml: run poetry install in backend/." >&2
    exit 1
fi
export VIRTUAL_ENV PATH="$VIRTUAL_ENV/bin:$PATH" PYTHONPATH="$PWD/backend:$PWD/plugins" OTEL_SDK_DISABLED=true

[[ -n ${check_only-} ]] && exec pre-commit run "$@"

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
