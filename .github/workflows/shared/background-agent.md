---
engine: copilot
runtimes:
  python:
    version: "3.13"
network:
  allowed:
    - defaults
    - python
    - node
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
  - name: Install pre-commit
    run: pip install pre-commit && pre-commit install-hooks
---

## How every background agent works

You are one of several scheduled background agents for the Data Product Portal. Your output is at most one finding per run, and only when you are highly confident it is real, significant and worth a maintainer's time. Producing nothing is a good outcome; a weak or wrong proposal is a bad one.

### 1. Learn the repository as it is today

Read `AGENTS.md`, `CONTEXT.md` and the `AGENTS.md` of every area you touch (for example `backend/AGENTS.md`, `frontend/AGENTS.md`). They define the domain language, conventions and commands. Discover the structure by exploring; never assume a path exists because it existed before. Never edit generated files (the AGENTS.md files name them).

### 2. Never repeat a proposal

Search all issues and pull requests, open and closed, with the label `background-agent`. A closed one without a merge means a maintainer rejected it: never propose the same thing, or a variation of it, again. Skip anything already tracked by any other open issue or PR as well.

### 3. Find, rank, keep one

Survey broadly before deciding. Collect candidates, rank them by real-world impact, and keep only the top one. A candidate must:

- be significant, not cosmetic or a matter of taste;
- be fixable with a small, focused change that does not add complexity or change behaviour beyond the fix;
- come with the evidence your role requires below.

### 4. Confidence gate

If the top candidate does not clearly pass every point above, or you cannot produce the evidence, stop and call `noop` with a one-line reason. Do not lower the bar to have something to show.

### 5. Fix and verify

Make the minimal change. Add the regression test or proof your role asks for. Run `pre-commit run --all-files` and the test suites of every area you changed (see the AGENTS.md files for the commands). Everything must pass. The PostgreSQL service is reachable at `host.docker.internal:5432`; set `POSTGRES_SERVER=host.docker.internal` and pass `-o env_override_existing_values=0` to pytest when running backend tests, otherwise `backend/.test.env` resets it to `localhost`. If you cannot get the checks green, call `noop` instead.

### 6. Report

Create exactly one issue and one draft pull request:

- Issue: what is wrong, where, the evidence, and the impact. Use the domain language from `CONTEXT.md`.
- Pull request: write the body following `.claude/skills/pr-description/SKILL.md` when it exists. Start the body with `Fixes #<temporary id of the issue>` and include the evidence and the test or proof output.
