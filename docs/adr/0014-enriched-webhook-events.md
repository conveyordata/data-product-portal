# Enriched Webhook Events (v2)

## Context and Problem Statement

The Portal backend fires a webhook after every mutating API call via an HTTP middleware (`backend/app/main.py`). The payload is a raw forward of the HTTP exchange:

```json
{
  "method": "POST",
  "url": "/api/v2/data_products",
  "query": {},
  "response": "{\"id\": \"abc-123\"}",
  "status_code": 200
}
```

This creates three problems:

1. **No semantic meaning.** There is no event name. Consumers pattern-match URLs to determine intent, which breaks silently when routes are renamed or versioned.
2. **Fires on failure.** The v1 middleware fires for all POST/PUT/DELETE responses regardless of status code, including 4xx and 5xx. Consumers receive "events" for operations that never succeeded.
3. **No embedded object.** The provisioner SDK (ADR-0013) was designed to deliver full domain objects to hook methods, but cannot do so as long as the backend only provides a minimal response body. A POST returns only `{"id": "..."}`, forcing a round-trip call back to the Portal.

We want a v2 event system that delivers named events with full domain objects embedded, fires only on success, and runs concurrently with v1 so existing provisioners are not broken.

## Decision Drivers

* **No disruption to v1.** Existing provisioners depend on the v1 middleware. It must continue to fire unchanged.
* **Success-only.** v2 events must fire only when the operation succeeded (HTTP 2xx). v1 fires even on errors.
* **Explicit and discoverable.** Reading a route handler should make it immediately obvious whether a v2 event fires, and for which named event. A grep should return a definitive list of all emitting endpoints.
* **Testable.** Each emitting endpoint must be testable in isolation without making real outbound webhook calls.
* **Full domain object in payload.** The event payload must include the complete hydrated Pydantic object, not just an ID.

## Considered Options

* **Option A: Enhanced Middleware** Extend the existing middleware to map `(method, url_path)` to an event name, re-query the DB for the full object, and fire a v2 payload alongside the existing v1 payload.
* **Option B: Dependency Annotation on Routes** Add `Depends(emit_event("data_product.created", ...))` to the `dependencies=[]` list of each route that should emit a v2 event, following the `Authorization.enforce()` pattern.
* **Option C: Service-Layer Emission** Inject a `WebhookEmitter` into services and call it after each successful write.

## Decision Outcome

**Chosen option: Option B — Dependency Annotation on Routes.**

Like all FastAPI dependencies, the event-emitting dependencies run as part of the same dependency graph as the authorization check — before the route handler body executes. Any developer who understands how authorization is expressed will immediately understand how v2 events are expressed. The three operation types — DELETE, UPDATE, and CREATE — each require slightly different handling.

**DELETE** uses `emit_event`. The dependency runs before the handler, fetches the full object by its path `id`, and schedules `call_v2_webhook` as a Starlette background task. Fetching before the handler is essential: by the time the handler body runs the row is gone. Success-only semantics come from Starlette: background tasks are tied to the successful response object. When the handler raises `HTTPException`, Starlette's exception handler returns a new error response that does not carry the queued background tasks, so the webhook never fires.

**UPDATE** uses `emit_event_after`, a yield dependency. Code before `yield` runs before the handler (no-op for UPDATE); code after `yield` runs after the handler has committed its changes. The dependency then re-fetches the object by path `id`, ensuring the event payload reflects the post-update state. Success-only semantics come from the `try/except/else` structure around `yield`: the webhook call is in the `else` branch and is skipped if the handler raised an exception.

**CREATE** also uses `emit_event_after`, but cannot re-fetch by `id` because a `POST` endpoint has no `id` path parameter and the object does not yet exist before the handler runs. Instead, the handler stores the newly created domain object in `request.state` before returning, and the dependency reads it from there in the post-`yield` phase. The same `try/except/else` structure ensures success-only semantics.

### Confirmation

- A new `WEBHOOK_V2_URL` setting is added to `backend/app/settings.py`.
- A new module `backend/app/core/webhooks/v2.py` provides `call_v2_webhook`, the `emit_event` dependency factory (for DELETE routes), and `emit_event_after` (a yield-based factory for UPDATE and CREATE routes).
- Routes that should emit v2 events are annotated with a `Depends(emit_event(...))` or `Depends(emit_event_after(...))` entry in their `dependencies=[]` list.
- The v1 middleware in `backend/app/main.py` is not changed.
- v2 events fire only on route success: for DELETE, Starlette discards background tasks when the handler raises `HTTPException`; for UPDATE and CREATE, the yield dependency's `try/except/else` skips the webhook call on any exception.

## Pros and Cons of the Options

### Option A: Enhanced Middleware

* **Good, because** the webhook concern stays in one file; no route handler changes are needed.
* **Bad, because** a `(method, url_path) → event_name` mapping table becomes a second source of truth that drifts from actual route definitions.
* **Bad, because** DELETE events are impossible to enrich: the object no longer exists in the database when the middleware runs.
* **Bad, because** it fires on failure; detecting success requires explicit status-code inspection per response, which is easy to get wrong.
* **Bad, because** the middleware does not have access to a DB session without injecting one separately; enriching the payload requires a round-trip DB query after the transaction has already committed.
* **Bad, because** the emitting logic is untestable at the individual route level; tests must manipulate the middleware globally.

### Option B: Dependency Annotation on Routes

* **Good, because** it matches the existing `Authorization.enforce()` pattern exactly.
* **Good, because** success-only semantics are mechanically guaranteed without any explicit status-code check in application code. For DELETE, Starlette discards background tasks when the handler raises `HTTPException`. For UPDATE and CREATE, the yield dependency's `try/except/else` skips the webhook call on any exception.
* **Good, because** annotated routes are self-documenting: the `dependencies=[]` list shows both the authorization requirement and the event contract in one place.
* **Good, because** a project-wide search for `emit_event` returns the complete catalogue of emitting endpoints.
* **Good, because** it is testable by patching `call_v2_webhook` or using `app.dependency_overrides` — the same mechanisms used for existing v1 webhook tests and auth overrides in `conftest.py`.
* **Good, because** DELETE works correctly: the dependency fetches the full object before the handler body deletes it.
* **Neutral, because** UPDATE and CREATE routes require a yield-based factory (`emit_event_after`) rather than the simpler `emit_event`. CREATE routes additionally require one line in the handler body to store the created object in `request.state`.
* **Neutral, because** each emitting route requires one additional entry in its `dependencies=[]` list.

### Option C: Service-Layer Emission

* **Good, because** the webhook call is co-located with the business operation.
* **Bad, because** services are transport-agnostic by convention: they accept a `Session` and return domain objects; they do not import HTTP concerns such as `BackgroundTasks` or `Request`.
* **Bad, because** `BackgroundTasks` is not available inside services; emitting with `asyncio.create_task()` directly would re-introduce the fire-on-failure risk of v1.
* **Bad, because** each service that emits events becomes harder to unit test since the emitter must be mocked at the service layer.

---

## Appendix A: Design Details

### New Settings

```python
# backend/app/settings.py
WEBHOOK_V2_URL: Optional[str] = None
```

`WEBHOOK_URL` and `WEBHOOK_SECRET` continue to control v1. When `WEBHOOK_V2_URL` is `None`, no v2 events fire. Both URLs can point to the same endpoint or different ones.

### New Module: `backend/app/core/webhooks/v2.py`

```python
from collections.abc import AsyncGenerator
import httpx
from fastapi import BackgroundTasks, Request
from pydantic import BaseModel
from app.settings import settings
from app.core.logging import logger


async def call_v2_webhook(event_name: str, payload: dict) -> None:
    url = settings.WEBHOOK_V2_URL
    if not url:
        return
    try:
        body = {"event": event_name, **payload}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=body)
            if resp.status_code != 200:
                logger.warning("v2 webhook returned %d", resp.status_code)
    except Exception as e:
        logger.warning("v2 webhook failed: %s", e)


def emit_event(event_name: str, extract) -> callable:
    """
    Dependency factory for DELETE routes.

    Runs before the handler. Fetches the object via `extract` (which receives
    the same kwargs as the route: DB session, path parameters, etc.) and
    schedules `call_v2_webhook` as a background task.

    Background tasks are tied to the successful response object. When the
    handler raises HTTPException, Starlette returns a new error response that
    does not carry the queued background tasks — so the webhook is never fired.

    Errors in the dependency itself are caught and logged so they never block
    the handler.

    The module-level variable gives a stable reference for dependency_overrides
    in tests.
    """
    async def _dependency(background_tasks: BackgroundTasks, **kwargs) -> None:
        try:
            if not settings.WEBHOOK_V2_URL:
                return
            obj: BaseModel = extract(**kwargs)
            key = event_name.rsplit(".", 1)[0]  # "data_product.deleted" → "data_product"
            payload = {key: obj.model_dump(mode="json")}
            background_tasks.add_task(call_v2_webhook, event_name, payload)
        except Exception as e:
            logger.warning("v2 webhook setup failed: %s", e)

    return _dependency


def emit_event_after(event_name: str, extract) -> callable:
    """
    Yield-based dependency factory for UPDATE and CREATE routes.

    Code before `yield` runs before the handler (nothing to do here). Code
    after `yield` runs after the handler has completed. The `else` branch of
    the try/except/else ensures the webhook only fires when the handler
    returned normally — any exception raised by the handler re-raises here,
    skipping the else block.

    UPDATE routes: `extract` re-fetches the object by path `id` after the
    handler commits, so the event payload reflects the post-update state.

        emit_event_after(
            "data_product.updated",
            lambda id, db, **_: DataProductService(db).get_data_product(id),
        )

    CREATE routes: `extract` reads from `request.state` because a POST
    endpoint has no `id` path parameter and the object does not exist before
    the handler runs. The handler must store the created object in
    `request.state` under an agreed key before returning.

        emit_event_after(
            "data_product.created",
            lambda request, **_: request.state.data_product,
        )

    Errors in the post-yield phase are caught and logged so they never affect
    the already-sent response.

    The module-level variable gives a stable reference for dependency_overrides
    in tests.
    """
    async def _dependency(**kwargs) -> AsyncGenerator[None, None]:
        try:
            yield
        except Exception:
            raise
        else:
            try:
                if not settings.WEBHOOK_V2_URL:
                    return
                obj: BaseModel = extract(**kwargs)
                key = event_name.rsplit(".", 1)[0]
                payload = {key: obj.model_dump(mode="json")}
                await call_v2_webhook(event_name, payload)
            except Exception as e:
                logger.warning("v2 webhook emit failed: %s", e)

    return _dependency
```

### Route Annotation Pattern

The three operation types use different factories for reasons explained in the Decision Outcome.

#### DELETE

`emit_event` fetches the object before the handler runs — essential because the row no longer exists after deletion.

```python
# backend/app/data_products/router.py

from app.core.webhooks.v2 import emit_event

_emit_data_product_deleted = emit_event(
    "data_product.deleted",
    lambda id, db, **_: DataProductService(db).get_data_product(id),
)

@router.delete(
    "/{id}",
    dependencies=[
        Depends(Authorization.enforce(Action.DATA_PRODUCT__DELETE, DataProductResolver)),
        Depends(_emit_data_product_deleted),
    ],
)
def remove_data_product(id: UUID, db: Session = Depends(get_db_session)) -> None:
    DataProductService(db).remove_data_product(id)
```

#### UPDATE

`emit_event_after` re-fetches the object after the handler commits, so the event payload reflects the post-update state.

```python
from app.core.webhooks.v2 import emit_event_after

_emit_data_product_updated = emit_event_after(
    "data_product.updated",
    lambda id, db, **_: DataProductService(db).get_data_product(id),
)

@router.put(
    "/{id}",
    dependencies=[
        Depends(Authorization.enforce(Action.DATA_PRODUCT__UPDATE, DataProductResolver)),
        Depends(_emit_data_product_updated),
    ],
)
def update_data_product(
    id: UUID,
    data_product: DataProductUpdate,
    db: Session = Depends(get_db_session),
) -> DataProductResponse:
    return DataProductService(db).update_data_product(id, data_product)
```

#### CREATE

`emit_event_after` is also used for CREATE, but the extract lambda reads from `request.state` instead of re-fetching by `id`. The handler must store the created object in `request.state` before returning.

```python
from app.core.webhooks.v2 import emit_event_after

_emit_data_product_created = emit_event_after(
    "data_product.created",
    lambda request, **_: request.state.data_product,
)

@router.post(
    "",
    dependencies=[
        Depends(Authorization.enforce(Action.GLOBAL__CREATE_DATAPRODUCT, EmptyResolver)),
        Depends(_emit_data_product_created),
    ],
)
def create_data_product(
    request: Request,
    data_product: DataProductCreate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> CreateDataProductResponse:
    created = DataProductService(db).create_data_product(data_product, authenticated_user)
    request.state.data_product = created
    return CreateDataProductResponse(id=created.id)
```

### v2 Payload Schema

Single-entity event:

```json
{
  "event": "data_product.created",
  "data_product": {
    "id": "3fa85f64-...",
    "name": "My Product",
    "namespace": "my-product",
    "status": "pending",
    "domain": { "id": "...", "name": "Finance" },
    "type": { "id": "...", "name": "Source Aligned" }
  }
}
```

Scoped event (output port, technical asset):

```json
{
  "event": "output_port.created",
  "data_product": { ... },
  "output_port": { ... }
}
```

The embedded objects are the existing `Get*Response` Pydantic schemas serialised with `model_dump(mode="json")`. No new schemas are introduced.

### Testability

Patch `call_v2_webhook` directly — the same pattern used by the existing v1 tests in `backend/tests/app/core/webhooks/test_webhook_middleware.py`:

```python
@patch("app.core.webhooks.v2.call_v2_webhook")
async def test_create_data_product_fires_v2_event(mock_webhook, client, payload):
    response = client.post("/api/v2/data_products", json=payload)
    assert response.status_code == 200
    mock_webhook.assert_awaited_once()
    event_name, event_payload = mock_webhook.call_args.args
    assert event_name == "data_product.created"
    assert event_payload["data_product"]["name"] == payload["name"]

@patch("app.core.webhooks.v2.call_v2_webhook")
async def test_failed_create_does_not_fire_v2_event(mock_webhook, client, invalid_payload):
    response = client.post("/api/v2/data_products", json=invalid_payload)
    assert response.status_code == 422
    mock_webhook.assert_not_awaited()
```

Alternatively, use `app.dependency_overrides[_emit_data_product_created]` with the module-level variable for per-test suppression. The same approach works for `emit_event_after`-based dependencies.

---

## Appendix B: Event Catalogue

All hooks in `BaseProvisioner` (ADR-0013 Appendix A) correspond to one v2 event name. The mapping is listed here for reference.

### Data Product Events

| Event name | Trigger endpoint |
|---|---|
| `data_product.created` | `POST /api/v2/data_products` |
| `data_product.updated` | `PUT /api/v2/data_products/{id}` |
| `data_product.deleted` | `DELETE /api/v2/data_products/{id}` |
| `data_product.about_updated` | `PUT /api/v2/data_products/{id}/about` |
| `data_product.status_updated` | `PUT /api/v2/data_products/{id}/status` |
| `data_product.setting_changed` | `POST /api/v2/data_products/{id}/settings/{setting_id}` |
| `data_product.team_member_added` | `POST /api/v2/authz/role_assignments/data_product` |
| `data_product.team_member_removed` | `DELETE /api/v2/authz/role_assignments/data_product/{id}` |
| `data_product.input_port_linked` | `POST /api/v2/data_products/{id}/link_input_ports` |
| `data_product.input_port_unlinked` | `DELETE /api/v2/data_products/{id}/input_ports/{input_port_id}` |

### Output Port Events

| Event name | Trigger endpoint |
|---|---|
| `output_port.created` | `POST /api/v2/data_products/{id}/output_ports` |
| `output_port.updated` | `PUT /api/v2/data_products/{id}/output_ports/{id}` |
| `output_port.deleted` | `DELETE /api/v2/data_products/{id}/output_ports/{id}` |
| `output_port.about_updated` | `PUT /api/v2/data_products/{id}/output_ports/{id}/about` |
| `output_port.status_updated` | `PUT /api/v2/data_products/{id}/output_ports/{id}/status` |
| `output_port.link_approved` | `POST .../output_ports/{id}/input_ports/approve` |
| `output_port.setting_changed` | `POST .../output_ports/{id}/settings/{setting_id}` |

### Technical Asset Events

| Event name | Trigger endpoint |
|---|---|
| `technical_asset.created` | `POST /api/v2/data_products/{id}/technical_assets` |
| `technical_asset.updated` | `PUT .../technical_assets/{id}` |
| `technical_asset.deleted` | `DELETE .../technical_assets/{id}` |
| `technical_asset.status_updated` | `PUT .../technical_assets/{id}/status` |
| `technical_asset.linked` | `POST .../output_ports/{id}/technical_assets/add` |
| `technical_asset.link_approved` | `POST .../technical_assets/approve_link_request` |
| `technical_asset.link_denied` | `POST .../technical_assets/deny_link_request` |
| `technical_asset.unlinked` | `DELETE .../technical_assets/remove` |
