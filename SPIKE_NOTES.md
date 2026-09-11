# Spike notes: ADR-0024 dynamic plugin system

Validates the mechanism in [docs/adr/0024-dynamic-plugin-system.md](docs/adr/0024-dynamic-plugin-system.md)
end to end: an external package (`plugins/example-azure-blob/`) implements
an Azure Blob Storage technical asset, discovered and run by the portal,
and creates a real, queryable technical asset through the portal's existing
`/v2/data_products/{id}/technical_assets` endpoints - not a parallel API.

## What a plugin author writes

A plugin is an ordinary, independently versioned Python package
(`plugins/example-azure-blob/` is the example). It:

- Depends on `data-product-portal-sdk` (for the base class below) and
  whatever else it needs for its own logic (here, just `sqlalchemy`, for its
  own table).
- Registers itself via a `data_product_portal.plugins` entry point pointing
  at its plugin class - nothing else to configure. Installing the package is
  enough for the portal to find it.
- Owns its own database table and Alembic migration history.
- Bundles its own icon (`icon.svg`, read via `importlib.resources`).

The portal never depends on a plugin, and a plugin never depends on the
portal - only on its SDK.

## The interface: `TechnicalAssetPlugin`

`sdk/sdk/plugins/base.py` defines `TechnicalAssetPlugin`, an ABC a plugin
class inherits from directly (alongside `sdk/sdk/plugins/context.py`'s
`PluginContext` - together this is a new, hand-written SDK subpackage,
following the same pattern as the existing `sdk/sdk/provisioner/`).

A plugin declares its identity as class attributes (`key`, `display_name`,
`icon_package`/`icon_resource`, `fields`, `target_revision`,
`migrations_package`, `model`) and implements three classmethods:
`validate`, `render_result`, `get_url`. `get_icon()` comes for free - it's a
generic default built from `icon_package`/`icon_resource`.

Real inheritance buys real developer ergonomics: `__init_subclass__` raises
a `TypeError` naming exactly which required attribute is missing, the
moment the plugin author's own class is defined - not silently skipped
later at discovery time. This was a deliberate reversal from an earlier
design where the interface was a `typing.Protocol` (structural typing, zero
dependency, but no help from an IDE or type checker, and a missing
attribute only caught much later). The ADR's Considered Options section
records both options and why inheritance won.

**Field vocabulary (`PluginField`)**: deliberately minimal - a plugin
describes its fields as plain data (`name`, `label`, `required`, an
optional regex `pattern`, `tooltip`), string type only for now. No portal
imports, no database access. This is intentionally *not* the old system's
full `UIElementMetadata` (select/radio/checkbox sub-configs, `depends_on`
conditionals, DB-driven option lists) - that would force every plugin
author to understand frontend concepts and depend on the portal's own ORM
and table shapes. The portal, not the plugin, owns a small adapter
(`PluginService._build_dynamic_plugin_metadata_response()`) that turns this
minimal vocabulary into the real `UIElementMetadataResponse` shape the
existing, metadata-driven create-technical-asset form already renders -
so a plugin shows up as a selectable tile with working, validated inputs,
and its author never writes frontend code.

**Context and call boundary**: alongside `values`, every plugin method call
gets a `PluginContext` (the technical asset's id/name, its output port, its
data product, its domain, and the acting user) - generic information a
plugin's logic might need, most notably the actor, since a plugin that
needs its own external credentials (an STS AssumeRole, for example - the
pattern the existing S3 plugin already uses) resolves them per-request,
scoped to that actor, rather than the portal storing any long-lived secret
on a plugin's behalf. Every call into a plugin goes through
`call_plugin()` (`backend/app/plugins/runtime.py`): an uncaught exception
is caught, logged with its stack trace, and turned into a clean error - one
broken plugin can't take down the request it's handling, and a plugin's own
exception message never leaks to the caller.

## Discovery

`backend/app/plugins/loader.py`'s `discover_plugins()` scans the
`data_product_portal.plugins` entry point group via
`importlib.metadata.entry_points()` - plain stdlib, not `pluggy`. A class
that fails to import, or isn't a real `issubclass()` of
`TechnicalAssetPlugin`, is logged and skipped rather than crashing startup
for every other plugin (a malformed plugin already fails earlier, at import
time, via `__init_subclass__`). No caching - entry points are cheap to
re-scan, and the plugin set can't change without a process restart anyway.

`pluggy` was deliberately not used: it composes *many* plugins'
implementations of the *same* hook (a call invokes every installed
plugin and aggregates results) - this system never composes anything, a
call for `azure-blob` only ever invokes the `azure-blob` plugin, a plain
`key -> class` lookup. Pluggy would solve a composition problem this system
doesn't have.

## Storage and migrations

Each plugin gets its own database table, migrated by its own Alembic
revisions - not a shared JSON column. One shared `env.py`
(`backend/app/plugins/alembic_runner/env.py`) serves every plugin; a plugin
author only ever writes `versions/*.py`.

- Isolation between plugins' migration histories comes from Alembic's
  `version_locations` option, scoped per plugin to just that plugin's own
  `versions/` directory.
- "One shared table tracks each plugin's currently-applied revision" (the
  ADR's requirement) is satisfied by pointing every plugin's Alembic
  `version_table` at the same physical table, `plugin_migration_state`,
  instead of Alembic's default per-environment table. Revision ids are
  unique, plugin-key-prefixed strings (`azureblob_0001_...`) by convention,
  so the shared table stays human-readable with no extra discriminator
  column.
- That shared table is pre-created by a core migration with a deliberately
  wide `version_num VARCHAR(255)` column, not left to Alembic's own
  default `VARCHAR(32)` - a real revision id (`azureblob_0003_drop_technical_asset_id`,
  39 characters) overflowed the default during testing.
- `MigrationContext.get_current_revision()` (the API in every Alembic
  tutorial) assumes one linear history and silently isn't usable against a
  table holding several plugins' independent histories at once. Use
  `get_current_heads()` instead, intersected with the specific plugin's own
  known revision ids, to find the one that's actually its current revision.
- `reconcile_plugin()` compares a plugin's declared `target_revision`
  against the table's current value and upgrades or downgrades as needed;
  `backend/app/db_tool.py`'s `migrate` command calls `reconcile_all()` after
  the core migration, in the same deploy step. A broken plugin migration
  propagates up into `db_tool migrate`'s existing top-level error handling
  and blocks the deploy, the same as a broken core migration would.

## Creating and reading a technical asset

A plugin-backed asset is created and read through the exact same
`/v2/data_products/{id}/technical_assets` endpoints every built-in type
already uses - not a separate, plugin-only API. (An earlier version of this
spike had its own parallel create/read endpoints to avoid touching the real
ones; that was reviewed and rejected, since it would mean two ways to
create and read a technical asset in every generated SDK/CLI/frontend
client, permanently.)

- `CreateTechnicalAssetRequest` / `GetTechnicalAssetsResponseItem` /
  `RenderTechnicalAssetAccessPathRequest` all have `platform_id`/
  `service_id`/`configuration` as `Optional` now, alongside a `plugin_key`/
  `values` alternative. A model validator enforces exactly one of
  (`configuration`) or (`plugin_key` + `values`) is given.
- `data_outputs` gained a nullable `plugin_key` column. A plugin-backed
  asset's own row lives in the plugin's own table, sharing its primary key
  with the `data_outputs` row it belongs to - no physical foreign key
  across migration histories (nothing enforces this at the database level;
  it's a convention the portal's own insert code upholds), but the same
  shared-id shape the old `configuration_id`-based system already used.
- `TechnicalAssetService.hydrate_plugin_values()` populates `values` on a
  response after `model_validate()`, since the plugin's row lives outside
  the portal's ORM graph and can't be picked up automatically.
- `result_string`/`technical_info` branch on `plugin_key`: a plugin-backed
  asset calls the plugin's own `render_result()` instead of rendering a
  stored template, and reports empty `technical_info` (no per-environment
  concept for a plugin that ignores that layer).
- Creation and reads go through `Authorization.enforce()` with the exact
  same action/resolver pattern the existing technical-asset router already
  uses - nothing plugin-specific added to authorization.

## Environments: reusing the existing table, not inventing a new one

A plugin can opt into the portal's existing environment picker (the
dropdown on the "Access data" tile) by declaring `has_environments = True`
on its class. This deliberately reuses the real `Environment` table and the
exact `{{}}` -> namespace substitution mechanism a built-in type's own
environment resolution already does (`app.core.aws.get_url._get_data_product_role_arn`),
rather than inventing a plugin-specific parallel concept - a direct choice
of "build on top of the existing platform/environment data model" over
"don't use it at all," both explicitly allowed by the ADR's own decision
drivers.

- `TechnicalAssetPlugin.has_environments: ClassVar[bool] = False` - a
  plugin opts in explicitly; nothing changes for a plugin that doesn't.
- `PluginContext` gained `environment` (the environment's name),
  `environment_context` (that `Environment` row's own `context` field,
  already namespace-substituted), and `namespace` - plain strings, not a
  database session or ORM object, so the plugin package itself still only
  ever depends on the SDK. The *portal's own service layer*
  (`PluginService._get_dynamic_plugin_url`) does the actual `Environment`
  lookup and substitution, on the plugin's behalf.
- Missing or unknown environment names fail exactly the way a built-in
  type's own environment resolution already does: a 400 if the plugin
  requires one and none was given, a 404 if the named environment doesn't
  exist - not a silent fallback.
- The example plugin sets `has_environments = True` and uses
  `environment_context` directly in `get_url()` (an Azure storage-account
  URL template with a namespace placeholder) - `sample_data.sql` already
  had unused `azure_development`/`azure_production` environment rows
  (empty `context`), now given a real template value to make this testable
  end to end.
- One real gotcha hit building this: `sample_data.sql` is itself
  Jinja2-templated (the `{{ var }}` placeholders throughout it, resolved by
  `db_tool`'s own seeding step) - a literal `{{}}` placeholder written
  directly into a seed value collides with that and fails to parse. Fixed
  by escaping it as `{{ "{{}}" }}` (a Jinja2 print statement whose output
  is the literal text `{{}}`), the same trick the AWS rows avoid needing
  only because their `{{}}` comes from an env var's value, not literal text
  in the file.

**Verified against a real seeded database, over real HTTP**, using the two
Azure environment rows: no `environment` query param on the plugin's
`get_url` → 400 with the plugin-specific message; an unknown environment
name → 404; `environment=azure_development` and `environment=azure_production`
both resolve to the correct, distinct, namespace-substituted URLs
(`https://<namespace>-dev.blob.core.windows.net/` vs.
`https://<namespace>-prd.blob.core.windows.net/`); `GET /v2/plugins/` and
`GET /v2/plugins/platform-tiles` both report `has_environments: true` for
`azure-blob`, which is what actually drives the frontend's existing
"Access data" tile to show the environment picker - no new frontend code
needed, the same way the field-vocabulary adapter needed none.

**Deliberately not built this round**: the built-in types' *other*
environment-driven mechanism - `PlatformServiceConfiguration`/
`env_platform_service_configs`, identifier-matched per environment, used
for `technical_info`'s per-environment strings and for a DB-backed `select`
field at creation time (`get_platform_options`) - stays out of reach for a
dynamic plugin. Only the `Environment`/`get_url` half was asked for and
built; a plugin-backed asset's `technical_info` is still empty.

## The generic API contract

The portal's published, generator-checked API description (what the
frontend client, Python SDK, and Go CLI are built from) is generated once,
at core-project release time - it can never describe a plugin's exact
fields, since a plugin might only be installed later, in a customer's own
image. So a technical asset's configuration is described generically in
that contract (`values: dict`), for every type, not just plugins. Anything
that needs a specific type's exact fields - form rendering, validation -
looks them up separately, at the moment it needs them (a runtime endpoint
call on the frontend side, a direct plugin method call on the backend
side), never from the generated types.

Verified directly, not just inferred from the spec: ran the actual SDK and
Go CLI generators against the OpenAPI spec with the plugin installed and
grepped the output for any plugin-specific name (`container_name`,
`azure-blob`, `example_azure_blob`) - zero matches in either generated
client. The only place `container_name`/`AzureBlob` appear in the spec at
all is the old, pre-existing, soon-to-be-replaced built-in Azure Blob
plugin schema - a different code path.

## The frontend: no new form components

The create-technical-asset form, its field rendering, the platform-tile
picker, and the live "resulting path" preview are already fully
metadata-driven - no per-type React components exist. Once a plugin is
exposed through the portal's adapter (above), it needs **no new
form-rendering code**: it appears as a tile, its fields render with
validation, entirely through the existing, generic components.

The one piece of real branching logic added anywhere in the frontend is in
`technical-asset-form.component.tsx`: on submit (and for the live preview),
if the selected tile is a dynamic plugin (checked against the plugin key
set from `useListPluginsQuery()`, not a fragile metadata flag), the
submitted `configuration.*` fields get repacked into `plugin_key`/`values`
before the request goes out. Everything else - which fields render, their
labels/tooltips/validation (`pattern` becomes a real antd validation rule),
the tile picker, the icon - needed zero plugin-specific frontend code.

A plugin's icon isn't a bundled frontend asset (it's only known at deploy
time) - `icon_name: "dynamic:<key>"` is a sentinel `icon-loader.ts`
recognizes, rendering an `<img>` that fetches
`{AppConfig.getApiBaseURL()}/api/v2/plugins/dynamic/<key>/icon` from the
backend directly, rather than a bundled SVG component.

## What's verified

- Discovery, migration (fresh install, upgrade, downgrade, no-op
  reconciliation), and the base interface's call boundary (validation
  failure, an unrelated crash, the happy path) - all against a real
  Postgres, via `python -m app.plugins.demo` and direct `psql` inspection.
- Real technical-asset creation and reads, end to end, against a real
  seeded database, through the real HTTP endpoints with real authorization
  checks: old-style creation unaffected, a pre-existing seed-data asset
  reads back byte-identical to before, and a plugin-backed asset creates,
  persists, and reads back correctly (including its computed
  `result_string`).
- The generic API contract: spec, Python SDK, and Go CLI generators all
  confirmed clean of plugin-specific names.
- The full browser flow, via Playwright against the real running frontend
  and backend: selecting the plugin's tile, seeing its fields render with
  validation, submitting, and seeing the created asset with a correctly
  loaded icon - this caught and led to fixing several bugs invisible at the
  API level alone (the dynamic-plugin tile-selection check, icon CSS
  sizing, and the icon URL resolving against the wrong origin in local
  dev).
- `ruff`, `ruff-format`, `mypy` (backend and SDK configs), `tsc --strict`,
  and `biome` all clean; the OpenAPI spec regeneration check confirms no
  accidental API surface changes from the interface-mechanism (Protocol ->
  ABC) change.
- Environment resolution (see "Environments" above): missing/unknown
  environment handling, and both seeded Azure environments resolving to
  correct, distinct URLs - all against a real seeded database, over real
  HTTP.

## What's deliberately deferred, not built

- **Boolean/select/conditional fields, DB-driven option lists** for a
  plugin's own fields - string-only for now, a documented gap, not an
  oversight.
- **Namespace/tags/access-mode/search-indexing** on a plugin-backed asset
  beyond the bare minimum needed to create one - real, separate work
  belonging to whoever formally picks up the technical-asset-relationship
  ADR.
- **Multi-plugin-per-package** was never actually exercised (one package,
  one plugin class, throughout this spike). The entry-point mechanism looks
  like it supports it with no extra portal-side work, but that's untested.
- **A documented external-credential pattern** for a plugin that needs its
  own login flow (STS AssumeRole and similar) - `PluginContext.actor`
  supports it, and the existing S3/Databricks/Snowflake plugins show the
  shape, but nothing about this is written down as guidance yet.
- **A `plugin_key` column on the shared `plugin_migration_state` table** -
  legibility today depends entirely on the revision-id-prefix convention,
  which nothing enforces.
- **A full audit of every place that reads a `TechnicalAsset`** and assumed
  `platform_id`/`service_id` were always populated - one concrete instance
  of this (an event-history panel) was found and fixed because it broke
  visibly; there may be others not yet exercised.
