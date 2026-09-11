# Dynamically Loadable Plugin System

**Status:** Proposed - draft for iteration, not yet accepted.

## Context and Problem Statement
The portal already lets data products connect to external platforms (S3, Snowflake, Postgres, Databricks, and others) through a plugin mechanism. Today, adding a brand-new one of these means: writing new code, creating a brand-new database table just for that one integration, writing a database migration to create that table, and editing a couple of internal registration lists - all inside the core project. Because all of that lives in the core project, adding an integration always means submitting a change to it (or forking it).

**Core question:** how should a plugin's code run, and how should a plugin's information be modeled and stored, so that adding one never requires a change to the core project?

Next to that I also want to highlight some context of what is out of scope and to think about those next steps. Currently,
plugins are used in a manner to translate portal concepts (Technical Assets) to an external system or link them to something that holds up in the "real world". It is not the job to actually create these resources (this is part of the provisioners' job). So in some way or form, the plugins translate the Portal core resources (technical asset/dataproducts) into real world concepts.
However, since the provisioner works separately from that, which is the resource that does both things again, it translates events, and actually creates or provisions those resources. In other words there is duplicate responsibility shared among concepts which needs to be cleared out.
The same holds for the concepts we use in Portal core such as `Platforms` and `PlatfomServices`, which currently are used in the plugin concept, but are not in the provisioner, which is a bit contradictory.

Important that these are NOT part of this ADR. These are follow-up work.


For reference, I use Portal Core to reference the source code in the main repo and plugin as the dynamically loadable plugin.

## Decision Drivers

* Adding or changing an integration should never require a database migration to portal core to any of the core project's own, non-plugin-specific tables.
* Adding an integration should never require submitting a change to the core project, or maintaining a fork of it.
* The portal should assist with migrations when a plugin needs to change its own configuration, rather than leaving that entirely to the plugin author.
* Whatever a plugin author has to do to add an integration should be as light as reasonably possible, without giving up the flexibility to add new functionality.
* Whatever is decided needs a realistic, low-disruption way to move the handful of integrations that already exist onto it, rather than leaving them permanently on a separate, older system.
* Simplicity beats defensiveness: given every customer runs their own separate, self-hosted copy of the portal, prefer the simplest option that works over one that defends against risks that don't apply to this deployment model.
* A plugin should be usable as soon as its package is installed - the portal discovers it automatically, without a separate step to name it.
* For a first version, this should be built on top of the platform, platform services, and environments data model as it exists today - or simply not use it at all. Redefining that model completely is out of scope here, but this decision shouldn't make it harder to change later.

## Out of scope
* Revising the core data model, including the per-environment infrastructure tables (`env_platform_configs`, `env_platform_service_configs`, `platform_service_configs`) - a separate ADR. These keep existing as they are; a plugin built under this decision can read them if it needs to. This also include the defenition of the relation shp with techincal asset and techincal asset type, is a plugin exactly that or not.
As this needs some work and is currently not exactly clear what the data model should be and is not.
* Still out of scope: the concrete data model a dynamically loaded plugin's technical asset settles into long-term (tags/access-mode compatibility rules specific to a plugin, search indexing, and similar). Two things *are* now decided and implemented, narrowing this: (1) see "How the API describes a plugin's configuration" - a dynamically loaded plugin's technical asset is created and read through the same `/v2/data_products/{id}/technical_assets` endpoints as every other type, not a separate plugin-specific API; and (2) what a plugin is allowed to say about its own fields for UI rendering purposes is deliberately small - see "The plugin's field vocabulary, and who owns turning it into a form" below - not the richer `UIElementMetadata` model the built-in types can use.
* An admin interface for managing integrations. Integrations (including the ones with no code) remain reachable only through the underlying data/API for now, matching how they're exposed to the rest of the interface today.
* Attaching integrations beyond data products. Integrations continue to attach to a data product's technical assets only.
* Logging, tracing, and observability conventions for plugin authors, beyond the portal catching exceptions at the plugin call boundary. Structured logging format, distributed tracing, and metrics for plugin calls are not addressed here.
* Concurrency aspects on replicas when running on a cluster setup.
* Tooling to test out alembic or database migrations of the plugin's own tables.
* Portal Core has no responsibility of keeping and storing permanent credentials for a plugin's own API calls. If a plugin needs to make authenticated calls, it can implement calls based on the user authenticated and making the plugin call.
* Setting up the proper `UIElementMetadata` for the plugin's own fields, beyond the minimal adapter that translates a plugin's declared list of string-typed fields into custom form fields.

## Considered Options

### Where the plugin's code runs

A real, versioned Python package, installed into the customer's own image, was the expected direction from the start - see "Loading the python packages inside portal core" below for how the portal actually discovers one.
The alternatives below are recorded for completeness

1. **Build it into the core project (today's situation)** - rejected, this is the exact problem being solved.
2. **Ship it as a separately installable package** - built and versioned like any other Python package, installed into the customer's own image.
   * **2a - discovered automatically**, via Python's standard package-registration mechanism.
   * **2b - discovered by explicit name** - the image author names exactly which modules to load, in one setting.
3. **Drop it into a scanned folder, loaded in-process** - the portal imports a plugin file directly at startup, no packaging needed.
4. **Drop it into a scanned folder, run as a separate program per call** - any language, isolates a broken plugin, but slower per call and more work to build.
5. **Run it inside the portal, in a locked-down sandbox** - safe by construction, but needs a new sandboxable-format runtime.
6. **Run it entirely on a separate server the plugin author operates** - 6a renders its own screen, 6b just answers questions for the portal's generic renderer.
7. **Build a public marketplace** - a way to find plugin code; could sit on top of any option above.

### Loading the python packages inside portal core

#### Option 1: Discover plugins automatically via Python entry points
- Python's standard entry-points mechanism - the same one Airflow's own classic plugin registration uses for operators, hooks, executors, and UI views. (Airflow separately uses `pluggy`'s hookspec/hookimpl system for its listener API, where many plugins can each optionally implement several lifecycle hooks - a different shape of problem than one class per plugin, so not a reason to pull `pluggy` in here.)
- Installing the package is enough - nothing extra to configure.
- Robust and well-established: this is what "advertise yourself as a plugin" means in the Python packaging ecosystem.
- Harder to see at a glance what's loaded, since nothing in the Dockerfile names it - it's implicit in whatever got installed.

#### Option 2: No automatic discovery, hardcode it through settings
- Easy to understand - one setting lists exactly what's loaded.
- More manual bookkeeping: installing a plugin isn't enough by itself, it also has to be named.
- Doesn't fit "just install it and it works."

### How the portal recognizes a plugin's shape

Once a plugin class is loaded (see "Loading the python packages inside portal core" above), the portal needs to know it actually has the right shape - the right class attributes and methods - before treating it as a real plugin.

#### Option 1: `typing.Protocol`, checked structurally
- The portal declares the shape as a `Protocol` (`@runtime_checkable`); a plugin class only needs to match it structurally - the same attribute and method names - not inherit from anything the portal ships.
- A plugin package never needs the portal, or even its SDK, as a dependency to be recognized.
- Nothing catches a plugin author missing a required attribute until the loader inspects the class at runtime (plain `hasattr` checks); there's no class to inherit from, so an IDE or type checker gives little help writing one.

#### Option 2: An ABC in the SDK, a plugin inherits from it
- `TechnicalAssetPlugin` lives in `sdk/sdk/plugins/`, alongside the SDK's other hand-written, non-generated code (`sdk/sdk/provisioner/`) - a plugin depends on the SDK, not the portal itself, the same way an event handler under `sdk.provisioner` already does.
- Real inheritance: autocomplete on the required methods, and a `TypeError` naming exactly which class attributes are missing, raised the moment the plugin author's own class is defined - not silently skipped later, at discovery time.
- A shared, non-abstract `get_icon()` default (reading `icon_package`/`icon_resource` via `importlib.resources`) comes for free through inheritance - a plugin no longer has to repeat it.
- Pulls in the SDK's own dependencies (`httpx`, `attrs`, `python-dateutil`, `fastapi`) - meaningfully heavier than Option 1's zero portal/SDK dependency.

### Where and how is the configuration of the plugin stored

A plugin's identity - its name, icon, and fields - lives directly on its own Python class, inherited from the portal's `TechnicalAssetPlugin` interface (see "How the portal recognizes a plugin's shape" above), alongside the configuration behavior described below; it isn't a separate thing to store. The icon is referenced as a bundled file path next to the plugin's own code, not inlined as a raw string.

#### Option 1: Single table for all plugins with a JSON column
- Needs a stored version per row, and some tooling to reload against it.
- Hard for migrations: a plugin author who changes a field has no real migration to write - either the portal builds a way to make that easier, or it's on the plugin author to deal with it defensively, in their own code.
- A lot of that defensiveness falls on plugin developers, since old, stored values don't automatically match a newer field declaration.
- Keeps the number of tables small - the fixed identity fields of every plugin type live in one shared table.
- Harder to index or join against, since the configured values themselves sit inside a JSON blob.

#### Option 2: Separate table for each plugin, plus one table tracking versions
Creating a table for each plugin - the schema can be partially defined by portal core (an id, a name, a version, ...) and partially self-defined by the plugin. This stays a single table per plugin, not a denormalized model.

Alongside that, one shared table tracks each plugin's table, its version, and its schema. Only the latest version needs to be kept there - older versions live in the plugin's own migration history, not in this tracking table.

- Comes with a built-in versioning system via Alembic - and this isn't custom machinery: Alembic already supports running multiple, independent migration histories side by side ("Run Multiple Alembic Environments" in its own docs), each with its own version-tracking table.
- Easier to put indexes and joins in place than against a JSON column.
- Lots of new tables, growing with however many plugins are installed.

 The core project's own migrations already run as a deploy-time step, before the app starts serving traffic . That same step extends to also walk every named plugin: each plugin's own class hardcodes the revision it wants (set by the plugin author, versioned right alongside its code, discovered the same way its identity is  the portal core compares that to the plugin's tracked current revision and reconciles the table to match, upgrading or downgrading as needed.

### How the API describes a plugin's configuration

Whichever storage option above is picked, the portal's published, generator-checked API description (the one the frontend client, Python SDK, and Go CLI are built from) is generated once, at core-project release time. It can't describe the exact fields of a plugin a customer only adds later, in their own image - so a technical asset's configuration has to be described as a generic value in that published contract, for every type, built-in or custom. Real validation still happens server-side; anything that needs a specific plugin's exact fields looks them up separately, at the moment it needs them.

#### Option 1: A single pair of API endpoints to fetch plugin information
- A GET endpoint for default plugin information: name, id, icon, etc.
- A GET endpoint that returns the rest as a JSON blob, by id.
- Writes and reads of a technical asset's actual configured values go through the existing, generic `/v2/data_products/{data_product_id}/technical_assets` endpoints - the same ones every built-in type already uses - not a dedicated plugin-specific create/read API. A plugin-only pair of endpoints (as the spike built, to avoid rewriting those existing endpoints while proving the storage/discovery mechanism) was considered as the long-term shape and rejected: it would mean two ways to create and read a technical asset in every generated SDK/CLI/frontend client, permanently, for the cost of skipping real, one-time work on the existing endpoints. This still requires `configuration` (or its generic replacement) on `CreateTechnicalAssetRequest`/`GetTechnicalAssetsResponseItem` to accept a generic value for a plugin-backed asset alongside the existing typed union for built-in ones - real implementation work, sized separately (see Out of scope).

#### Option 2: Dedicated endpoints per plugin
- Would mean a new endpoint per plugin, built-in or custom - but a build-time-generated endpoint can't exist yet for a plugin that isn't installed at build time, so this contradicts the "generic value for every type" answer above. Not pursued further.

### The plugin's field vocabulary, and who owns turning it into a form

The existing create-technical-asset form is already metadata-driven end to end: it renders whatever fields a `UIElementMetadata` response describes (string/select/radio/checkbox, conditional visibility via `depends_on`, dynamically fetched select options, namespace defaults, ...), the same code path for every built-in type. For a plugin's fields to show up as a selectable tile with working inputs, *something* has to translate the plugin's own field descriptions into that shape.

The question is where that richness is allowed to come from. Part of it - concretely, a built-in type's `select` options can come from querying the portal's own database (`PlatformServiceConfiguration` rows for a given platform key) - is backend behavior, not just a UI description.

#### Option 1: A minimal, string-only field vocabulary
- A plugin's own field vocabulary is plain data - no portal imports, no database access: a list of string fields, each with a `name`, `label`, `required`, and an optional `pattern` (a regex, checked both client- and server-side). A string covers most of what an integration actually asks for (a bucket name, a database connection string, a Glue database name, ...).
- The portal, not the plugin, owns a small adapter that turns this into the same `UIElementMetadataResponse` shape the existing form already consumes, so a plugin appears as a tile and its fields render with zero new frontend code.
- Brings the most value for the least work: one field type covers most real integrations, and nothing about it depends on the platform/platform-service data model.
- Boolean and select field types, conditional fields, and DB-backed dynamic options aren't supported - a plugin that genuinely needs one of those can't be added yet.

#### Option 2: Full `UIElementMetadata` parity
- A plugin produces the full `UIElementMetadata` shape itself - select/radio/checkbox sub-configs, `depends_on` conditionals, DB-driven option lists.
- Requires real, additional backend and frontend work to support authoring and validating that richer shape generically, for a plugin nobody has written yet.
- Requires every plugin author to understand frontend-shaped concepts (form field types, conditional visibility) and, for anything DB-backed like `select` options, to depend on the portal's ORM and exact table shapes - directly against the "as light as reasonably possible" decision driver: a plugin already depends on the SDK for its base class, but the portal's own ORM and database are a different, heavier kind of dependency this decision explicitly avoids. Not pursued for a first version.

### Whether a plugin's access URL can vary by environment

The existing "Access data" tile shows an environment picker (dev/production/...) before resolving a technical asset's access URL, for any type whose metadata declares `has_environments`. Built-in types (e.g. S3) resolve that per-environment: the chosen environment's own `Environment.context` (a template string, with `{{}}` substituted for the data product's namespace) decides what `get_url` actually returns - for S3 that's an IAM role ARN used to assume a role and build a federated console URL.

#### Option 1: No environment concept for a dynamic plugin
- `has_environments` stays hardcoded `false` for every dynamic plugin; the "Access data" tile never shows an environment picker for one, and `get_url` never receives an environment.
- Simplest, and matches "a plugin never depends on the portal's own database" as closely as possible.
- A plugin genuinely can't distinguish "give me the URL for staging" from "give me the URL for production" - not a viable option for any plugin whose real-world resource actually differs by environment (most integrations this system targets do).

#### Option 2: Reuse the portal's existing `Environment` table
- A plugin opts in with `has_environments: ClassVar[bool] = True`. The portal resolves the chosen environment's `Environment` row and its `context` template exactly the way it already does for a built-in type, substitutes the data product's namespace into it the same way, and hands the plugin the result (plus the raw environment name and namespace) via `PluginContext` - not a raw database session or ORM object, so the plugin package itself still never depends on the portal's ORM.
- Reuses the actual, existing data - the same `environments` table and the same `{{}}` -> namespace substitution built-in types already rely on - rather than inventing a plugin-specific parallel concept, per this ADR's own decision driver to build on top of the existing platform/environment data model rather than avoid it.
- Zero new tables, zero new migrations - `Environment` already exists and is already managed by admins the same way for every type, built-in or dynamic.
- The *portal's own service layer* now depends on `Environment` on a dynamic plugin's behalf - a plugin can no longer be reasoned about as touching nothing but its own table; it can trigger a lookup against core, non-plugin-owned data. Deliberately accepted: the alternative (no environment support at all) fails a driver more directly than this fails "as light as possible."


- Loading the python packages inside portal core: Option 1 - automatic discovery via Python entry points.
- How the portal recognizes a plugin's shape: Option 2 - an ABC (`TechnicalAssetPlugin`), living in the SDK's `sdk.plugins` package, that a plugin class inherits from.
- Where and how is the configuration of the plugin stored: Option 2 - a dedicated table per plugin, migrated by the plugin's own Alembic revisions.
- How the API describes a plugin's configuration: Option 1, with the published contract describing configuration generically for every type, served through the existing technical-asset endpoints rather than a dedicated plugin-only API.
- The plugin's field vocabulary, and who owns turning it into a form: Option 1 - a minimal, string-only vocabulary (`name`, `label`, `required`, an optional regex `pattern`), adapted by the portal into the existing `UIElementMetadataResponse` shape.
- Whether a plugin's access URL can vary by environment: Option 2 - a plugin can opt in to the portal's existing `Environment` table and its `{{}}` -> namespace substitution, the same mechanism built-in types already use.

### Confirmation

This decision is reflected in the application by:

* A new integration is added by installing it as a package into the customer's own image, with no change to the core project and no fork of it - discovered automatically via its entry point, no separate naming step required.
* A plugin's own identity lives directly on its Python class, right alongside its code - the icon is a bundled file path. The portal defines this shape as `TechnicalAssetPlugin`, an ABC in the SDK's `sdk.plugins` package - a plugin class inherits from it directly, so it gets real autocomplete and a `TypeError` naming any missing required attribute the moment its own class is defined, rather than only being checked structurally at discovery time. A plugin package depends on the SDK, not the portal itself, to be recognized.
* A technical asset's specific, filled-in values live in a table that belongs to that plugin, migrated by the plugin's own Alembic revisions; a shared table tracks which revision each plugin's table is currently at, and `python -m app.db_tool migrate` reconciles both core and plugin tables to their declared target revision (upgrading or downgrading as needed) in the same existing deploy step.
* The portal's published API description treats a technical asset's configuration lazily, and as a generic value for every type; anything needing a type's exact fields looks them up separately, at the moment it needs them.
* The API regarding technical assets is not different for dynamically loaded plugins and is read through the same `/v2/data_products/{data_product_id}/technical_assets` endpoints every built-in type already uses, not a separate, plugin-only API - so there is exactly one way to create or read a technical asset in every generated SDK/CLI/frontend client, regardless of which system backs it.
* A plugin's own field vocabulary (see "The plugin's field vocabulary, and who owns turning it into a form") is deliberately smaller than the built-in types' `UIElementMetadata` - string fields with an optional regex `pattern`, nothing that needs portal database access. The portal owns the adapter that turns this into a real, selectable tile with working, validated inputs in the existing form - a plugin author never writes frontend code, and never has to for a plugin to be usable through the portal's own UI.
* Existing integrations move onto the new interface one at a time; both the old, table-per-type mechanism and the new, plugin-owned-table mechanism are supported until the last one moves.
* Running a customer's own plugin code safely is that customer's own responsibility; the portal does not add sandboxing, code review, or resource limits as part of this decision.
* Calls into a plugin's code are wrapped by the portal at the call boundary: an uncaught exception is caught, logged with its stack trace, and surfaced as a clean error, so one broken plugin can't take down the request it's handling.
* Alongside its own `values`, a plugin's methods are passed a context object carrying whatever's generic across every technical asset type (its own id/name, its output port, its data product, its domain).
* A plugin that declares `has_environments = True` gets a real environment picker on its "Access data" tile, the same as a built-in type. The portal resolves the chosen environment against the existing `Environment` table, substitutes the data product's namespace into its `context` field the same way a built-in type's environment resolution already does, and passes the result to the plugin's `get_url` via `PluginContext` (`environment`, `environment_context`, `namespace`) - plain strings, not a database session, so the plugin package itself still depends only on the SDK. Calling without an environment (when required) or naming one that doesn't exist fails the same way a built-in type's own environment resolution already does (400 / 404), not a silent fallback.
* If a plugin's own validation is backed by a dynamically-built model (e.g. Pydantic) for nicer error messages, that model stays internal to `validate` - it never becomes part of the generated OpenAPI schema, SDK, or CLI types.

## Pros and Cons of the Options

### Loading the python packages inside portal core - Option 1: automatic, via entry points
- **Good, because** installing the package is enough - nothing extra to configure or forget.
- **Good, because** it's a standard, well-understood Python mechanism, not something built from scratch.
- **Bad, because** anything already installed - including a dependency nobody chose on purpose - could advertise itself the same way and get loaded; what's running is only visible in the dependency tree, not the Dockerfile.

### Loading the python packages inside portal core - Option 2: explicit naming through settings
- **Good, because** nothing loads that wasn't named on purpose - reviewable in one setting.
- **Bad, because** it doubles the bookkeeping: install and name are two separate steps, and forgetting the second fails silently.

### How the portal recognizes a plugin's shape - Option 1: `typing.Protocol`
- **Good, because** a plugin package never needs the portal, or even its SDK, as a dependency to be recognized.
- **Bad, because** a plugin author gets no help from an IDE or type checker writing one, and a missing attribute is only caught later, at discovery time, not when the plugin's own class is defined.

### How the portal recognizes a plugin's shape - Option 2: an ABC in the SDK
- **Good, because** a plugin author gets real inheritance: autocomplete on the required methods, and a `TypeError` naming exactly what's missing, raised immediately at class-definition time.
- **Good, because** a generic default (`get_icon()`) comes for free through inheritance, instead of every plugin repeating it.
- **Bad, because** it pulls in the SDK's own dependencies (`httpx`, `attrs`, `python-dateutil`, `fastapi`) - meaningfully heavier than Option 1's zero dependency.

### Where and how is the configuration of the plugin stored - Option 1: single JSON column
- **Good, because** no migration is ever needed to add or change an integration.
- **Bad, because** validating at save time doesn't help with rows already saved under an older version of a plugin's fields - every plugin author defensively guesses at a shape they can't fully trust.
- **Bad, because** a plain database query against one specific field, across every technical asset using it, becomes a more roundabout query against the JSON blob instead.

### Where and how is the configuration of the plugin stored - Option 2: dedicated table per plugin, Alembic-migrated
- **Good, because** a migration can reshape or backfill old data as part of the same change that needs it - something the JSON column can't do.
- **Good, because** it reuses the deploy-time migration step the core project already runs; no new infrastructure needed to apply it.
- **Good, because** running several independent migration histories side by side is a documented Alembic pattern, not something built from scratch.
- **Bad, because** every field change now needs a real, shipped migration, authored by the plugin - more work than editing a declared field.
- **Neutral, because** uninstalling a plugin doesn't clean up its table - it's left in place, untouched, with nothing else happening; picked up again if the plugin is reinstalled.

### The plugin's field vocabulary, and who owns turning it into a form - Option 1: minimal, string-only vocabulary
- **Good, because** a plugin author writes plain data - no frontend knowledge, no portal-database access - and gets a working, validated form field for free.
- **Good, because** the portal-owned adapter means zero new frontend code is needed to add a plugin; it appears as a tile in the existing form automatically.
- **Bad, because** a plugin that genuinely needs a boolean, a dropdown, a conditional field, or a DB-driven option list can't have one yet - real, separate work to add later.

### Whether a plugin's access URL can vary by environment - Option 1: no environment concept
- **Good, because** a plugin stays fully isolated from the portal's own database - nothing to resolve, nothing to get wrong.
- **Bad, because** a plugin whose real-world resource genuinely differs by environment (most of them) simply can't express that - not a viable option long-term.

### Whether a plugin's access URL can vary by environment - Option 2: reuse the existing `Environment` table
- **Good, because** it reuses real, already-admin-managed data instead of inventing a plugin-specific parallel concept.
- **Good, because** the plugin itself still only ever sees plain strings via `PluginContext` - the database lookup and namespace substitution stay in the portal's service layer, not leaked into the plugin's own dependencies.
- **Bad, because** the portal's service layer now touches core, non-plugin-owned data on a dynamic plugin's behalf - a plugin can no longer be reasoned about as touching only its own table.

### The plugin's field vocabulary, and who owns turning it into a form - Option 2: full `UIElementMetadata` parity
- **Good, because** a plugin could offer the same richness the built-in types have - booleans, dropdowns, conditional fields, DB-driven option lists - nothing permanently out of reach.
- **Bad, because** it requires real, additional backend and frontend work to support authoring and validating that richer shape generically, for a plugin nobody has written yet.
- **Bad, because** it requires every plugin author to understand frontend-shaped concepts (form field types, conditional visibility) and, for anything DB-backed like `select` options, to depend on the portal's ORM and exact table shapes - directly against the "as light as reasonably possible" decision driver. Not pursued for a first version.
