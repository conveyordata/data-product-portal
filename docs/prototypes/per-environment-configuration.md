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
- `PUT .../environment-configuration` replaces the base values and the full override set in one request.
- Saving queues the entity's normal id-only event, like any other change. The provisioner fetches the configuration and converges every environment itself. There is no apply step, no applied state and no pending diff: rolling out dev first means saving a dev override first.
- Authorization: the same action that guards updating the entity.

### UI

On the instance's detail page, a "Configuration" tab holds a matrix:

- Rows are the overridable properties. Columns are "Base" and one column per environment of the Data Product.
- Every cell is a select over the allowed values. Environment cells also offer "Inherit", the default, which shows the inherited base value greyed out. A cell with an override is visibly marked.
- One "Save" button saves the whole matrix.

## Not in scope

Apply per environment, approval flows, promote-to-prd, scheduling, applied-state tracking, tests, production-grade error handling.

## This branch: overrides on Technical Assets

### Domain choices

- The instance is a Technical Asset. The type is its plugin.
- A plugin marks a configuration field as overridable on the field itself: `engine_version: Annotated[str, EnvOverridable(label=..., allowed_values=(...))] = "16"`. The name comes from the field and the default from its default value, so each setting is declared once. `get_env_overridable_properties()` derives the list from the fields. The create form gets a select per property from that list, and `GET /api/v2/plugins/` returns it as `env_overridable_properties`, so a client can see what a type allows without a Data Product. The SDK generator strips the `Annotated` marker. Any plugin can opt in; only PostgreSQL does.
- Base values are ordinary columns of the plugin's configuration (`engine_version`, `size`, `storage_gb` on `postgresql_technical_asset_configurations`), so the create form sets them and they are part of the Technical Asset's `configuration` in every API response.
- Overrides live in one core table, `technical_asset_environment_overrides`, one row per (Technical Asset, environment, property) with a string value. Deleting the Technical Asset or the environment cascades.
- Environments are the Data Product's `environments`, never a hard-coded list.
- `GET` wraps the list as `{"properties": [...]}`. `PUT` takes `{"base_values": {name: value}, "overrides": {environment_id: {name: value}}}` and returns the same shape as `GET`. Base values that are left out of `base_values` keep their current value. An environment absent from `overrides` loses all its overrides.
- Saving queues `technical_asset.event` (`id`, `data_product_id`), the same event as any other Technical Asset change.
- The Configuration tab only shows when the asset's plugin metadata (from `/api/v2/plugins`) has an overridable field.

### File map

- Plugin declaration: `backend/app/technical_asset_configuration/base_schema.py`
- PostgreSQL showcase: `plugins/portal_plugins/postgresql/{model,schema}.py`, `plugins/portal_plugins/postgresql/versions/postgresql_0002_overridable.py`
- Override table: `backend/app/data_products/technical_assets/model.py`, `backend/app/database/alembic/versions/2026_10_23_1200-8b1e4f2c9a37_technical_asset_environment_overrides.py`
- API: `backend/app/data_products/technical_assets/{router,service,schema_request,schema_response}.py`
- UI: `frontend/src/pages/technical-asset/components/technical-asset-tabs/configuration-tab/configuration-tab.tsx`, `technical-asset-tabs.tsx`, `technical-asset.page.tsx`, the select default in `frontend/src/components/data-products/technical-asset-form/technical-asset-configuration-form.component.tsx`, cache tags in `frontend/src/store/api/services/tags/dataProductsTechicalAssetsTags.ts`

### Impact

What was easy:

- Everything fits the existing Technical Asset module: three endpoints, three service methods, one table. No new concept, no new router, no new permission.
- Plugins already describe their form through `UIElementMetadata`, so one flag plus a select default was enough to declare overridable fields generically.
- The base value comes for free: it is a normal configuration column, set by the create form and returned with the asset.
- Events needed no new type: saving queues the existing `technical_asset.event`.

What was awkward:

- A base value lives in a plugin-owned table while its overrides live in a core table. A plugin that wants overridable fields needs a plugin migration for the columns, and the two halves of one setting are stored in two places.
- Plugin configurations aren't in the OpenAPI spec, so the frontend can't type the base fields. The matrix only works through the dedicated endpoint.
- Settings that really belong to the platform per environment (engine version for all PostgreSQL databases in prd, say) would have to be repeated on every Technical Asset. This shape only fits settings that differ per asset.
- Alembic's version table limits revision ids to 32 characters, which a descriptive plugin revision name easily exceeds.

What I'd change:

- Store base values in the same override table under a null environment, so the plugin needs no migration and one row type holds the whole setting.
