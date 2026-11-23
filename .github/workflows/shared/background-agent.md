---
engine: copilot
env:
  FASTEMBED_CACHE_PATH: /tmp/gh-aw/fastembed
runtimes:
  python:
    version: "3.14"
network:
  allowed:
    - defaults
    - python
    - node
    - go
tools:
  edit:
  bash: [":*"]
  github:
    toolsets: [default]
services:
  postgres:
    image: pgvector/pgvector:0.8.0-pg17
    env:
      POSTGRES_PASSWORD: abc123
      POSTGRES_USER: postgres
      POSTGRES_DB: data_product_portal_test
    options: >-
      --health-cmd pg_isready
      --health-interval 2s
      --health-timeout 2s
      --health-retries 25
    ports:
      - 5432:5432
safe-outputs:
  threat-detection:
    post-steps:
      - name: Require the survey table
        run: |
          f=/tmp/gh-aw/agent_output.json
          [ -f "$f" ] || exit 0
          text=$(jq -r '.items[] | select(.type=="noop") | .message' "$f")
          [ -n "$text" ] || exit 0
          { echo "## Survey"; echo; echo "$text"; } >> "$GITHUB_STEP_SUMMARY"
          rows=$(printf '%s\n' "$text" | grep -c '^|' || true)
          if [ "$rows" -lt 9 ]; then
            echo "::error::noop without a survey table with a row per check ($rows table lines)"
            exit 1
          fi
  github-app:
    client-id: ${{ vars.APP_ID }}
    private-key: ${{ secrets.APP_PRIVATE_KEY }}
steps:
  - name: Install Poetry
    uses: snok/install-poetry@a783c322200f0519c7926aa6faa857c4e23e9263 # v1.4.2
    with:
      version: '2.4.1'
      virtualenvs-create: true
      virtualenvs-in-project: true
  - name: Install Task
    uses: go-task/setup-task@a00fbb05ce67b35648be3c78cbc9fd85354c757e # v2.2.0
  - name: Install backend dependencies
    run: task setup:backend
  - name: Setup Node.js
    uses: actions/setup-node@820762786026740c76f36085b0efc47a31fe5020 # v7.0.0
    with:
      cache: 'npm'
      cache-dependency-path: frontend/package-lock.json
      node-version-file: frontend/package.json
  - name: Install frontend dependencies
    run: task setup:frontend
  - name: Install pre-commit
    run: pip install -r .github/requirements-pre-commit.txt --require-hashes && pre-commit install-hooks
  - name: Preload embedding model
    working-directory: backend
    run: mkdir -p $FASTEMBED_CACHE_PATH && poetry run python -m app.embed
---

## How every background agent works

You are one of several scheduled background agents for the Data Product Portal. Every run should leave the codebase better than you found it: clearer, more consistent, or less likely to break. A change does not have to be big to be worth making. It has to be better, and you have to show why with evidence. Taste and unsupported opinion never count.

### 1. Learn the repository as it is today

Read `AGENTS.md`, `CONTEXT.md` and the `AGENTS.md` of every area you touch (for example `backend/AGENTS.md`, `frontend/AGENTS.md`). They define the domain language, conventions and commands. Discover the structure by exploring; never assume a path exists because it existed before. Never edit generated files (the AGENTS.md files name them).

### 2. Never repeat a proposal

Search all issues and pull requests, open and closed, with the label `background-agent`. A closed one without a merge means a maintainer rejected it: never propose the same thing, or a variation of it, again. Skip anything already tracked by any other open issue or PR as well.

### 3. Go through the checks, fix the first finding

Go through your role's required survey below in order. Read the files; a grep alone is not a check. Count each variant separately, never as one bucket. Stop at the first candidate that qualifies and fix it.

A candidate qualifies when both are true:

- It makes the code better and you can show it. It breaks a written rule in an `AGENTS.md`, `CONTEXT.md` or `.claude/skills/portal-design/SKILL.md`, or it diverges from a canonical file your role names, or your role's evidence proves it (a failing test, a measurement, a screenshot). A divergence from a written rule is worth fixing by definition. Never reject it as cosmetic, minor or a matter of taste.
- The fix is small and focused. It changes no behaviour beyond the fix, adds no complexity and introduces no new pattern. If the divergence is too wide for one reviewable PR, fix one coherent slice and list the rest.

### 4. When to noop

Call `noop` only when every check in your survey found no qualifying candidate, or when you cannot get the checks in step 5 green. The noop message must contain a Markdown table with one row per check: what you looked at, what you found and why it did not qualify. A noop without it fails the run. "Too small" and "cosmetic" are not reasons. "Too wide" means fix a slice.

### 5. Fix and verify

Make the minimal change. Add the regression test or proof your role asks for. Run `pre-commit run --files <the files you changed>` and the test suites of every area you changed (see the AGENTS.md files for the commands). Everything must pass. Poetry is not on your PATH: the backend dependencies are installed in `backend/.venv`, so wherever the docs say `poetry run python`, use `backend/.venv/bin/python` instead (for example `.venv/bin/python -m pytest` from `backend/`). The `regen-openapi-spec` hook calls `poetry` itself, so when you changed backend Python files run its export yourself from `backend/` with `set -a && source .test.env && set +a && .venv/bin/python -m app.open_api_export ../docs/static/openapi.json`, then run pre-commit with `SKIP=regen-openapi-spec` and include `docs/static/openapi.json` and any regenerated files in your change. The PostgreSQL service is reachable at `host.docker.internal:5432`; set `POSTGRES_SERVER=host.docker.internal` and pass `-o env_override_existing_values=0` to pytest when running backend tests, otherwise `backend/.test.env` resets it to `localhost`. If you cannot get the checks green, call `noop` instead.

### 6. Report

Create exactly one issue and one pull request:

- Issue: what is wrong, where, the evidence, and the impact. Use the domain language from `CONTEXT.md`. Pick a temporary id of the form `aw_` plus 3 to 8 letters or digits (for example `aw_fix1`) and pass it as the `temporary_id` argument of `create_issue`. Name the survey check the finding belongs to.
- Pull request: read `.claude/skills/pr-description/SKILL.md` first and write the body with exactly its sections, in its order and with its headings. Start the body with `Fixes #<the same temporary id>` (for example `Fixes #aw_fix1`) and put the evidence and the test or proof output under the matching sections. The id is only replaced by the real issue number if you passed it to `create_issue`; otherwise the merged PR leaves the issue open and that open issue stops every later run of this agent.
