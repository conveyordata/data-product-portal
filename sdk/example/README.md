# Example provisioner

A minimal, runnable provisioner that demonstrates the SDK's Kubernetes-operator-style
reconcile loop (`sdk.reconcile`).

It exposes a FastAPI webhook that receives portal CloudEvents
(`exploration.created` / `exploration.updated` / `exploration.deleted`) and enqueues a
**reconcile** for the affected exploration. Reconciliation is **level-based**: on each
event it re-fetches the exploration from the portal and converges an external resource
toward it. Here that resource is a per-exploration directory with a `manifest.json`
(under `PROVISIONER_WORKSPACE`, default `./.workspace`) — a stand-in for whatever real
infrastructure you would manage.

Key behaviours inherited from the reconcile loop:

- **Coalescing** — multiple events for the same exploration collapse into a single
  reconcile.
- **Debounce** — a short delay (2s here) before an exploration is picked up.
- **Concurrency** — 4 workers, but one exploration is never reconciled twice at once.
- **Backoff** — failed reconciles are retried with exponential backoff.

## Run it

Prepare:
```bash
cd sdk
poetry install --all-groups
```

Run:
```bash
PORTAL_BASE_URL="http://localhost:5050" PROVISIONER_WORKSPACE="./.workspace" \
  poetry run uvicorn example.provisioner:app --reload
```

Then point the portal's webhook (`WEBHOOK_V2_URL`) at:

```
http://localhost:8000/webhook
```

Create/update/delete an exploration in the portal and watch manifests appear, update,
and disappear under `PROVISIONER_WORKSPACE`. `GET /healthz` returns a simple liveness
check.

## What to look at

- `provisioner.py`
  - `ExplorationProvisioner(Reconciler)` — the level-based `reconcile(exploration_id)`.
  - `lifespan` — builds the API client, starts a `ReconcileManager` with workers, and
    wires a `ReconcileEventHandler`.
  - `POST /webhook` — hands the request to `handler.dispatch_routing(...)`.
