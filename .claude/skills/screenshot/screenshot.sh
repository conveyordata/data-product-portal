#!/usr/bin/env bash
set -euo pipefail

compare=""
if [[ ${1:-} == --compare ]]; then
    compare=$2
    shift 2
fi
out=$1
shift
mkdir -p "$out"

pages=()
for page in "$@"; do
    case $page in
        *=*) pages+=("$page") ;;
        home) pages+=("home=/") ;;
        *) pages+=("$page=/$page") ;;
    esac
done

skill="$(cd "$(dirname "$0")" && pwd)"
shoot() {
    npx -y -p playwright@1.56.0 -c \
        "NODE_PATH=\$(dirname \$(dirname \$(which playwright))) node '$skill/shoot.cjs' '$1' '$out' '$2' ${pages[*]}"
}

shoot http://localhost:3000 ""

if [[ -n $compare ]]; then
    local_file() {
        local file="$(git rev-parse --show-toplevel)/frontend/$1"
        [[ -e $file ]] || file="$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")/frontend/$1"
        echo "$file"
    }
    git fetch -q origin "$compare" || true
    ref="$(git rev-parse --verify -q "origin/$compare" || git rev-parse --verify "$compare")"
    src="$(mktemp -d)"
    git archive "$ref" frontend | tar -x -C "$src"
    ln -s "$(local_file node_modules)" "$src/frontend/node_modules"
    cp "$(local_file public/config.js)" "$src/frontend/public/"
    (cd "$src/frontend" && exec npx vite --port 3001 --strictPort --open false) >"$src/vite.log" 2>&1 &
    vite=$!
    trap 'kill $vite 2>/dev/null || true' EXIT
    until curl -sf -o /dev/null http://localhost:3001; do
        kill -0 $vite 2>/dev/null || { cat "$src/vite.log" >&2; exit 1; }
        sleep 1
    done
    shoot http://localhost:3001 ".${compare//\//-}"
fi
