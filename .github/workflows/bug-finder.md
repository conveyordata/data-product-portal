---
name: "Background agent: Bug finder"
description: Finds bugs and keeps them in the bug list in docs/bugs.md for the team to triage
on:
  schedule: weekly on wednesday
permissions:
  contents: read
  issues: read
  pull-requests: read
timeout-minutes: 60
runs-on: ubuntu-24.04
engine: copilot
sandbox:
  agent:
    runtime: docker-sudo-iptables
checkout:
  fetch: ["refs/pulls/open/*"]
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
  - name: Preload embedding model
    working-directory: backend
    run: mkdir -p $FASTEMBED_CACHE_PATH && poetry run python -m app.embed
safe-outputs:
  github-app:
    client-id: ${{ vars.APP_ID }}
    private-key: ${{ secrets.APP_PRIVATE_KEY }}
  report-failure-as-issue: false
  create-pull-request:
    draft: false
    title-prefix: "[bug list] "
    labels: [agent-bug]
    github-token-for-extra-empty-commit: none
  push-to-pull-request-branch:
    target: "*"
    required-title-prefix: "[bug list] "
    required-labels: [agent-bug]
  noop:
    report-as-issue: false
---

# Bug finder

Find bugs in the Data Product Portal and keep them in the bug list, `docs/bugs.md`. Never fix a bug: the team triages the list and decides what to fix.

## 1. Start from the current list

Search for an open pull request with the label `agent-bug`. If there is one, check out its branch and work on its `docs/bugs.md`: people triage in that pull request, so their edits to risks and statuses must stay as they are. Otherwise work on `docs/bugs.md` from the default branch.

Read the list. Never add a bug that is already in it, in any status, or a variation of it. A `rejected` row is a decision of the team: never add it again.

## 2. Learn the repository

Read `AGENTS.md`, `CONTEXT.md` and the `AGENTS.md` of every area you look at. Look across backend, plugins, frontend, SDK and CLI. Skip generated code: the API client in `frontend/src/store/api/`, the SDK models and `docs/static/openapi.json`.

## 3. Find bugs

A bug is code that does the wrong thing for a realistic input or state. Kinds of bug to look for, examples, not a complete list:

1. The same value stored or compared in two forms: an enum by name against by value, local time against UTC, an id against a name.
2. Writes that go through a read filter (visibility, soft delete, scope) and so skip or break on rows the caller can't see.
3. Data copied from a source of truth that isn't updated when the source changes, expires or is deleted.
4. Ranges, durations and versions that overlap or meet at an edge: the first or last day, or two active records where the code expects one.
5. Actions allowed or blocked in the wrong state, and guards that count the wrong states.
6. Input the API accepts that later breaks a lookup or ends in a 500.
7. Responses that don't match their declared schema, and clients that read fields the schema doesn't have.
8. Mutations that don't refresh the data they change, and state derived from props or queries that isn't reset when they change.
9. Errors caught and logged where the caller needs the failure.
10. A recent dependency bump or change whose effect wasn't followed through everywhere it reaches.

Every bug you add needs concrete evidence: where it is, the input or state that triggers it, and what happens against what should happen. Where practical, prove it with a test that fails on the current code; run it, but don't commit it. A suspicion without a trigger is not a bug. Add at most 10 new bugs per run, the highest risk first.

Give each bug a risk as defined at the top of `docs/bugs.md`, judged by what happens to a user, not by how hard the code is.

## 4. Check the open bugs

For every `open` row, check whether it still happens. If the code changed and it no longer does, set it to `fixed` and link the pull request or commit that fixed it in the notes.

## 5. Update the list

Add each new bug as a row with the next free ID (`BUG-001`, `BUG-002`, ...; never reuse one), status `open`, today's date as found, and a link to the code in the notes. Keep rows in ID order. Change nothing else in the file and no other file.

## 6. Report

- An open `agent-bug` pull request: commit the change on its branch and push it with `push_to_pull_request_branch`, with that pull request's number.
- None open: create one with `create_pull_request`, titled with the date.

In both cases the pull request body, or the commit message for a push, lists each new bug with its evidence and test output, and each bug that is now fixed. Use the domain language from `CONTEXT.md`.

If you found no new bugs and none was fixed, call `noop` with what you looked at.

## Running checks

Poetry is not on your PATH: the backend dependencies are installed in `backend/.venv`, so use `.venv/bin/python -m pytest` from `backend/`. The PostgreSQL service is reachable at `host.docker.internal:5432`; set `POSTGRES_SERVER=host.docker.internal` and pass `-o env_override_existing_values=0` to pytest, otherwise `backend/.test.env` resets it to `localhost`.
