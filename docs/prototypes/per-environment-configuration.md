# Prototype: per-environment configuration

Throwaway prototype for the Notion story "Per environment asset config" (IMEC). It exists to compare two places in the domain model where the same behaviour can live. It is not production code and will not be merged.

- Branch `prototype/env-overrides-technical-assets`: the behaviour lives on Technical Assets.
- Branch `prototype/env-overrides-tools`: the behaviour lives on a new Tool concept, a Platform comes from the plugin package and contributes Tool types and Asset types, and the Platform Service and environment config tables are rewritten into Platform × Environment settings.

## Shared behaviour (identical on both branches)

The behaviour below must be the same on both branches. Only where it lives in the domain differs.

### Overridable properties

A type (a plugin) declares which of its properties can be overridden per environment. Each overridable property has a name, a label, a closed list of allowed values and a default.

Showcase, PostgreSQL:

| name | label | allowed values | default |
| --- | --- | --- | --- |
| `engine_version` | Engine version | `15`, `16`, `17` | `16` |
| `size` | Size | `small`, `medium`, `large` | `small` |
| `storage_gb` | Storage (GB) | `20`, `50`, `100` | `20` |

Values are strings.

### Base values and overrides

- An instance has a base value for each overridable property. It is set when the instance is created (the type's default unless the user picks another value) and can be changed later.
- An instance can have an override per environment per property, only for environments its Data Product runs in (`data_product_environments`).
- Effective value for an environment = the override when present, else the base value.
- Validation, answered with HTTP 400 and a clear message: a value outside the allowed values, an override for a property that isn't overridable, an override for an environment the Data Product doesn't run in.

### API

- `GET .../environment-configuration` returns, per overridable property: name, label, allowed values, default, base value, and per environment of the Data Product (id, name, acronym): the override (or null) and the effective value.
- `PUT .../environment-configuration` replaces the base values and the full override set in one request. Saving only records the desired state. It doesn't trigger provisioning.
- `POST .../environments/{environment_id}/apply` queues one webhook event for that environment only. Payload: `id`, `data_product_id`, `environment` (acronym) and `configuration` (property name → effective value for that environment). The event type is `<entity>.environment_configuration_applied`.
- No applied state is stored and there is no pending diff. The Portal sends the event; keeping infrastructure in sync is the provisioner's job.
- Authorization: the same action that guards updating the entity.

### UI

On the instance's detail page, a "Configuration" tab holds a matrix:

- Rows are the overridable properties. Columns are "Base" and one column per environment of the Data Product.
- Every cell is a select over the allowed values. Environment cells also offer "Inherit", the default, which shows the inherited base value greyed out. A cell with an override is visibly marked.
- One "Save" button saves the whole matrix.
- Each environment column has an "Apply" button that calls the apply endpoint and shows a success message naming the environment.

## Not in scope

Approval flows, promote-to-prd, scheduling, applied-state tracking, tests, production-grade error handling.

## This branch: Tools, platforms from plugins

### Domain choices

- A Platform is declared in the plugin package (`plugins/portal_plugins/platforms.py`) as a subclass of `app.plugins.platform.Platform` and registered through the `data_product_portal.platforms` entry point. It carries a key, a display name, an icon, a Pydantic settings model, the Technical Asset types it contributes (`asset_types`) and the Tool types it contributes (`tool_types`). The API exposes both as `types` with a `kind` of `asset` or `tool`.
- Today's plugins are grouped by their former `parent_platform`: `aws` (S3, Glue, Redshift, Parameter Store), `azure` (Blob), and one platform per remaining plugin (`databricks`, `snowflake`, `postgresql`, `osi`). `parent_platform`, `has_environments` and `show_in_form` are gone from `PlatformMetadata`; discovery binds each asset type to its platform (`asset_type.platform`).
- GitHub, Conveyor and Agno are platforms without environments that contribute one Tool type without overridable properties (`GitHubPlugin`, `ConveyorPlugin`, `AgnoPlugin`, so `ENABLED_PLUGINS` keeps working). Their "open in" tiles still work because `get_url` moved from the asset type to the platform. A platform tile shows when any of its types is enabled.
- `platforms`, `platform_services`, `platform_service_configs`, `env_platform_configs`, `env_platform_service_configs` and `data_outputs.platform_id/service_id` are replaced by `platform_environment_settings` (platform key, environment id, settings JSON). The JSON is validated by the platform's settings model on write. The per-service shapes (S3 bucket, Glue database, and so on) live in `plugins/portal_plugins/settings.py`; each asset type reads its list from the settings field named after its `platform_key` (`s3`, `glue`, `postgresql`, ...).
- Form dropdown options are the identifiers found in that list across all environments. Templates come straight from the asset type's `PlatformMetadata`. Technical info per environment renders against the settings of each environment the Data Product runs in.
- A Tool (`backend/app/data_products/tools/`) belongs to one Data Product and stores the platform key, the Tool type name and the base values. Overrides live in `tool_environment_overrides`, one row per tool and environment. A Tool is never linkable to an Output Port: there is no link table.
- Tool types are offered when their name is in `ENABLED_PLUGINS`, like asset types. The PostgreSQL platform contributes `PostgreSQLInstance` with the spec's three properties.
- Authorization: Tool writes (create, delete, PUT environment-configuration, apply) use `DATA_PRODUCT__UPDATE_TECHNICAL_ASSET`, the action that guards Technical Asset writes. Reads use `HIDDEN__DATA_PRODUCT__READ`. The platform settings endpoints use `GLOBAL__UPDATE_CONFIGURATION`.
- Apply queues `tool.environment_configuration_applied` with `context.queue_event`, delivered by the existing webhook dispatcher.

### API

- `GET/PUT /api/v2/configuration/platforms/{platform_key}/environments/{environment_id}/settings`, `GET /api/v2/configuration/platforms`.
- `GET/POST /api/v2/data_products/{data_product_id}/tools`, `GET/DELETE .../tools/{id}`.
- `GET/PUT .../tools/{id}/environment-configuration`: `{"properties": [{name, label, allowed_values, default, base_value, environments: [{id, name, acronym, override, effective_value}]}]}`. PUT takes `{"base_values": {...}, "overrides": {environment_id: {...}}}`; base values left out keep their value, environments left out lose their overrides.
- `POST .../tools/{id}/environments/{environment_id}/apply`.

### File map

Backend core:
- `backend/app/plugins/platform.py`: `Platform`, `ToolType`, `OverridableProperty`.
- `backend/app/plugins/registry.py`: discovers platforms, derives asset types, resolves Tool types.
- `backend/app/configuration/platforms/`: `platform_environment_settings` model, service and router.
- `backend/app/technical_asset_configuration/base_schema.py`, `service.py`: options from settings, tiles and URLs per platform.
- `backend/app/data_products/technical_assets/`: no platform or service ids, technical info from platform settings.
- `backend/app/data_products/tools/`: model, router, service, request and response schemas.
- `backend/app/core/webhooks/events.py`: `ToolEnvironmentConfigurationAppliedEvent`.
- Migrations `5b1e7c2d9a40` (settings table, best-effort data move, drops the old tables) and `8c4d2f6a1b93` (tools).

Plugin package:
- `plugins/portal_plugins/platforms.py`, `plugins/portal_plugins/settings.py`, `plugins/pyproject.toml` (entry points), the asset type schemas, `glue/mcp_tools.py`.

Frontend:
- `frontend/src/pages/data-product/components/data-product-tabs/tools-tab/`: Tools tab and create modal.
- `frontend/src/pages/tool/`: Tool page and `ConfigurationMatrix`.
- `frontend/src/pages/settings/components/settings-tabs/platform-tab/`: platform list and JSON editor per environment.
- `frontend/src/components/data-products/technical-asset-form/technical-asset-form.component.tsx`: no platform or service ids.

Demo: `demo/*/portal_seed.sql`, `demo/*/provisioner/provisioner/reconciler.py`, `demo/basic/.env.portal`.

### Impact

What was easy:
- The override behaviour itself. A Tool is a fresh table owned by core, so base values, overrides and validation need no plugin migration and no change to the asset tables.
- Grouping assets under a platform removed code: the shared `get_url` rule for children of a parent tile, `PlatformServiceService.ensure_for_plugins` and the startup sync of platform rows all disappear.
- Settings as one validated JSON document per platform and environment make the admin screen a generic JSON editor.

What was awkward:
- The rewrite is wide. Five tables, two foreign keys, the technical info join, dropdown options, the AWS, Databricks and Snowflake links, the seeds, both demo provisioners, the generated SDK, CLI and client and a large part of the backend test harness all touched the old tables. Most of the diff is that rewrite, not Tools.
- Technical info no longer comes from a SQL join. The service attaches the matching settings rows to each asset, because the platform of an asset is only known through the plugin registry.
- Settings sections are found by naming convention (the asset type's `platform_key`, with dashes as underscores). It keeps the migration trivial but is implicit.
- Dropdown options that had no per-environment settings are lost in the migration: options are now derived from settings, not stored separately.
- The AWS sign-in URL never read `env_platform_configs`; it reads the role template from `environments.context`, so it is unchanged.
- Tool types and asset types are declared differently: asset types are classes with their own tables and Alembic history, Tool types are plain values on the platform.

What I would change:
- Give asset types the same overridable-property declaration as Tool types, so both kinds share one override mechanism and a Technical Asset could become a Tool's child later.
- Make the settings section explicit on the asset type instead of deriving it from `platform_key`.
- Split the platform rewrite and Tools into separate changes; the rewrite stands on its own.

### Not done, or not verified

- The migration has no downgrade.
- The backend test suite was not run: it uses its own database, outside the scratch database this prototype was limited to. Tests that covered removed tables were deleted; the remaining harness was adapted to platforms but not executed. Technical info tests were deleted, not rewritten.
- The developer guide (`docs/docs/developer-guide/adding-integrations.md`) still describes the old entry point group.
- A Tool type that is disabled after Tools exist makes their configuration endpoints answer 400.
