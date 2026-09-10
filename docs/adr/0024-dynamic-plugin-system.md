# Dynamically Loadable Plugin System

**Status:** Proposed - draft for iteration, not yet accepted.

## Context and Problem Statement

The portal already lets data products connect to external platforms (S3, Snowflake, Postgres, Databricks, and others) through a plugin mechanism. Today, adding a brand-new one of these means: writing new code, creating a brand-new database table just for that one integration, writing a database migration to create that table, and editing a couple of internal registration lists - all inside the core project. Because all of that lives in the core project, adding an integration always means submitting a change to it (or forking it).

**Core question:** how should a plugin's code run, and how should a plugin's information be modeled and stored, so that adding one never requires a change to the core project?

## Decision Drivers

* Adding or changing an integration should never require a database migration to any of the core project's own, non-plugin-specific tables.
* Adding an integration should never require submitting a change to the core project, or maintaining a fork of it.
* The portal should assist with migrations when a plugin needs to change its own configuration, rather than leaving that entirely to the plugin author.
* Whatever a plugin author has to do to add an integration should be as light as reasonably possible, without giving up the flexibility to add new functionality.
* Whatever is decided needs a realistic, low-disruption way to move the handful of integrations that already exist onto it, rather than leaving them permanently on a separate, older system.
* Simplicity beats defensiveness: given every customer runs their own separate, self-hosted copy of the portal, prefer the simplest option that works over one that defends against risks that don't apply to this deployment model.
* A plugin should be usable as soon as its package is installed - the portal discovers it automatically, without a separate step to name it.
* For a first version, this should be built on top of the platform, platform services, and environments data model as it exists today - or simply not use it at all. Redefining that model completely is out of scope here, but this decision shouldn't make it harder to change later.

## Out of scope
* Revising the core data model, including the per-environment infrastructure tables (`env_platform_configs`, `env_platform_service_configs`, `platform_service_configs`) - a separate ADR. These keep existing as they are; a plugin built under this decision can read them if it needs to, or ignore them entirely.
* The relationship between a plugin and a data product's technical asset type, including the concrete API endpoint shapes for reading and writing a technical asset's configured values - a separate ADR.
* An admin interface for managing integrations. Integrations (including the ones with no code) remain reachable only through the underlying data/API for now, matching how they're exposed to the rest of the interface today.
* Attaching integrations beyond data products. Integrations continue to attach to a data product's technical assets only.
* Logging, tracing, and observability conventions for plugin authors, beyond the portal catching exceptions at the plugin call boundary (see Confirmation). Structured logging format, distributed tracing, and metrics for plugin calls are not addressed here.
* Concurrency aspects on replicas when running on a cluster setup
* Tooling to test out aleembic or database migrations of the plugin's own tables.

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

### Where and how is the configuration of the plugin stored

A plugin's identity - its name, icon, and fields - lives directly on its own Python class, alongside the configuration behavior described below; it isn't a separate thing to store. The icon is referenced as a bundled file path next to the plugin's own code, not inlined as a raw string - the portal reads it via `importlib.resources` (the standard way to read a non-Python file shipped inside a package, working the same whether it's installed normally or as a zipped wheel), so nothing about identity needs a database row for a plugin that has code at all.

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

 The core project's own migrations already run as a deploy-time step, before the app starts serving traffic - the Helm `initContainer` and the `docker-compose` startup command both call `python -m app.db_tool migrate`. That same step extends to also walk every named plugin: each plugin's own class hardcodes the revision it wants (set by the plugin author, versioned right alongside its code, discovered the same way its identity is - via `importlib.resources`, not a documented folder path); the portal compares that to the plugin's tracked current revision and reconciles the table to match, upgrading or downgrading as needed. No new deploy-time mechanism, just more for the existing one to do.

### How the API describes a plugin's configuration

Whichever storage option above is picked, the portal's published, generator-checked API description (the one the frontend client, Python SDK, and Go CLI are built from) is generated once, at core-project release time. It can't describe the exact fields of a plugin a customer only adds later, in their own image - so a technical asset's configuration has to be described as a generic value in that published contract, for every type, built-in or custom. Real validation still happens server-side; anything that needs a specific plugin's exact fields looks them up separately, at the moment it needs them. The exact endpoint shapes below are part of the plugin/technical-asset relationship question under Out of scope, and aren't decided here.

#### Option 1: A single pair of API endpoints to fetch plugin information
- A GET endpoint for default plugin information: name, id, icon, etc.
- A GET endpoint that returns the rest as a JSON blob, by id.
- Whether a POST endpoint belongs here, or writes go through technical-asset-specific endpoints instead, is part of the relationship question above.

#### Option 2: Dedicated endpoints per plugin
- Would mean a new endpoint per plugin, built-in or custom - but a build-time-generated endpoint can't exist yet for a plugin that isn't installed at build time, so this contradicts the "generic value for every type" answer above. Not pursued further.


### How existing plugins move onto the new system

#### Option 1: Move everything over in one coordinated piece of work
Every existing plugin's stored values are copied, once, from its current dedicated table into its new, plugin-owned table. Every existing plugin's code is rewritten against the new interface at the same time. Done together, in one release.

#### Option 2: Run both systems side by side for a transition period
Old, table-per-type plugins and new, plugin-owned-table plugins coexist for a while, and plugins move over one at a time. Every piece of generic code that touches a technical asset's configuration (rendering a result, validating a form, exposing it through the API) has to handle both shapes until the last old plugin is moved, which reintroduces, temporarily, the exact kind of duplicated, parallel logic this whole change exists to remove.

## Decision Outcome
- Where the plugin's code runs: an installable Python package.
- Loading the python packages inside portal core: Option 1 - automatic discovery via Python entry points.
- Where and how is the configuration of the plugin stored: Option 2 - a dedicated table per plugin, migrated by the plugin's own Alembic revisions.
- How the API describes a plugin's configuration: Option 1, with the published contract describing configuration generically for every type.
- How existing plugins move onto the new system: Option 2 - side by side, one at a time.

Entry points need no separate naming step, at the cost of anything already installed being able to advertise itself - accepted here since every customer builds and owns their own image, and installing something is itself already a deliberate act.

Existing plugins move over side by side rather than all at once: with the platform/environment data model and the technical-asset relationship both out of scope here, what's left to move per plugin is small enough to verify on its own schedule.

### Confirmation

This decision is reflected in the application by:

* A new integration is added by installing it as a package into the customer's own image, with no change to the core project and no fork of it - discovered automatically via its entry point, no separate naming step required.
* A plugin's own identity (name, icon, fields) lives directly on its Python class, right alongside its code - the icon is a bundled file path, read via `importlib.resources`, not inlined as a string.
* A technical asset's specific, filled-in values live in a table that belongs to that plugin, migrated by the plugin's own Alembic revisions; a shared table tracks which revision each plugin's table is currently at, and `python -m app.db_tool migrate` reconciles both core and plugin tables to their declared target revision (upgrading or downgrading as needed) in the same existing deploy step.
* The portal's published API description treats a technical asset's configuration as a generic value for every type; anything needing a type's exact fields looks them up separately, at the moment it needs them.
* Existing integrations move onto the new interface one at a time; both the old, table-per-type mechanism and the new, plugin-owned-table mechanism are supported until the last one moves.
* Running a customer's own plugin code safely is that customer's own responsibility; the portal does not add sandboxing, code review, or resource limits as part of this decision.
* Calls into a plugin's code are wrapped by the portal at the call boundary: an uncaught exception is caught, logged with its stack trace, and surfaced as a clean error, so one broken plugin can't take down the request it's handling.
* Alongside its own `values`, a plugin's methods are passed a context object carrying whatever's generic across every technical asset type (its own id/name, its output port, its data product, its domain); its own data-model shape is still the deferred technical-asset-relationship ADR's to decide.
* If a plugin's own validation is backed by a dynamically-built model (e.g. Pydantic) for nicer error messages, that model stays internal to `validate` - it never becomes part of the generated OpenAPI schema, SDK, or CLI types.

## Pros and Cons of the Options

### Loading the python packages inside portal core - Option 1: automatic, via entry points
- **Good, because** installing the package is enough - nothing extra to configure or forget.
- **Good, because** it's a standard, well-understood Python mechanism, not something built from scratch.
- **Bad, because** anything already installed - including a dependency nobody chose on purpose - could advertise itself the same way and get loaded; what's running is only visible in the dependency tree, not the Dockerfile.

### Loading the python packages inside portal core - Option 2: explicit naming through settings
- **Good, because** nothing loads that wasn't named on purpose - reviewable in one setting.
- **Bad, because** it doubles the bookkeeping: install and name are two separate steps, and forgetting the second fails silently.

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

### How existing plugins move onto the new system - Option 2: side by side
- **Good, because** each plugin can move on its own schedule, verified independently.
- **Bad, because** every piece of generic code touching a technical asset's configuration has to handle both the old and the new shape until the last plugin moves.

## Implementation Spike: Open Questions

This decision fixes the direction; the following need a working spike to validate before this ADR can be accepted:

* **Shared Alembic runner vs. per-plugin Alembic environment.** Alembic's own "multiple environments" pattern assumes each one brings its own `alembic.ini` + `env.py` - real ceremony to ask of every plugin author. Validate whether the portal can instead provide one generic runner that all plugins share, with a plugin author only ever writing `versions/*.py` revision files, and what that runner actually looks like.
* **Isolating one plugin's revision chain from another's**, so two unrelated plugins' migrations can't collide or produce a confusing multi-head state - each plugin needs its own `ScriptDirectory`, pointed only at its own `versions/` folder.
* **Failure semantics.** If a plugin's migration throws mid-way, does `db_tool migrate` abort the whole deploy (matching how a failed core migration already blocks the deploy today), or continue past it? Should match existing behavior - fail loud, block the deploy.
* **A minimal, core-mandated schema for a plugin's own table** - the fields portal core requires the plugin to have regardless of its own content (an id, a foreign key back to the technical asset it belongs to, a version, ...) - needs to exist even before the deferred technical-asset-relationship ADR settles the rest.
* **The shape of the context object** passed to a plugin's methods alongside `values`. Airflow's operators are a useful reference point here: `execute(self, context)` receives ambient information about the current run (`dag`, `task_instance`, `dag_run`, ...) formalized as its own `Context` type, entirely separate from XCom (which exists only to pass arbitrary data *between* tasks, reached via `context["ti"].xcom_pull(...)`, and has no equivalent need here). The spike should settle the minimal, generically-useful set of fields for this system's own context object - starting candidates: the technical asset's own id/name, its output port, its data product, its domain.
* **One package defining more than one plugin class** - does each plugin class get its own migration namespace, or do multiple plugins in one package share one?
