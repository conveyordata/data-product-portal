# Dynamically Loadable Plugin System

**Status:** Proposed - draft for iteration, not yet accepted.

## Context and Problem Statement
Data Product Portal already lets data products connect to external platforms (S3, Snowflake, Postgres, Databricks, and others) through a plugin mechanism. Today, adding a brand-new one of these means: writing new code, creating a brand-new database table just for that one integration, writing a database migration to create that table, and editing a couple of internal registration lists - all inside the core project. Because all of that lives in the core project, adding an integration always means submitting a change to it (or forking it).

**Core question:** how should a plugin's code run, and how should a plugin's information be modeled and stored, so that adding one never requires a change to the core project?

This ADR also surfaces related context that is deliberately out of scope, to be picked up as follow-up work. Today, plugins translate Portal core concepts (technical assets) into something that holds up in the "real world" - they are not responsible for actually creating those resources, that is the provisioner's job. The provisioner, however, does both: it translates events *and* provisions the resulting infrastructure, so the same translation responsibility is duplicated across two concepts. The same tension exists for `Platforms` and `PlatformServices`: the plugin concept relies on them, but the provisioner does not, which is inconsistent.

These are not part of this ADR; they are follow-up work.


For reference, in this ADR we will use Portal Core to reference the source code in the main repo and plugins as the dynamically loadable plugin.

## Decision Drivers

* Adding or changing an integration should never require a database migration to portal core to any of the core project's own, non-plugin-specific tables.
* Adding an integration should never require submitting a change to the core project, or maintaining a fork of it.
* Data Product Portal should assist with migrations when a plugin needs to change its own configuration, rather than leaving that entirely to the plugin author.
* Whatever a plugin author has to do to add an integration should be as light as reasonably possible, without giving up the flexibility to add new functionality.
* Whatever is decided needs a realistic, low-disruption way to move the handful of integrations that already exist onto it, rather than leaving them permanently on a separate, older system.
* Simplicity beats defensiveness: given every customer runs their own separate, self-hosted copy of the portal, prefer the simplest option that works over one that defends against risks that don't apply to this deployment model.
* A plugin should be usable as soon as its package is installed - the portal discovers it automatically, without a separate step to name it. It won't scan at runtime though, things need to be available a boot time
* For a first version, this builds on top of the platform, platform service, and environment data model as it exists today - in practice, a plugin that reads real infrastructure state needs at least environments, and usually platforms too. Redefining that model completely is out of scope here (see "Out of scope"), but this decision shouldn't make it harder to change later.

## Out of scope
* Revising the core data model, including the per-environment infrastructure tables (`env_platform_configs`, `env_platform_service_configs`, `platform_service_configs`) - a separate ADR. These keep existing as they are; a plugin built under this decision can read them if it needs to. This also includes the definition of the relationship with technical asset and technical asset type.
This will be a next ADR
* The concrete, long-term data model for a plugin's technical asset (tags/access-mode compatibility rules, search indexing, and similar) is out of scope.
* API changes are out of scope: current endpoints are already generic, so they are reused as-is for plugins.
* Frontend rendering changes are out of scope: the portal reuses the `UIElementMetadata` class as-is for a plugin's fields, the same as every other technical asset type (see "UI rendering of a plugin's fields and form").
* An admin UI interface for managing integrations. Integrations (including the ones with no code) remain reachable only through the underlying data/API for now, matching how they're exposed to the rest of the interface today.
* Plugins only support custom technical assets.
* Logging, tracing, and observability conventions for plugin authors, beyond the portal catching exceptions at the plugin call boundary. Structured logging format, distributed tracing, and metrics for plugin calls are not addressed here.
* Portal Core has no responsibility of keeping and storing permanent credentials for a plugin's own API calls. If a plugin needs to make authenticated calls, it can implement calls based on the user authenticated and making the plugin call.
* Curating exactly which subset of portal core a plugin actually needs, rather than exposing all of it as a package - see "Distributing portal core as an installable Python package" below. Revisit once the existing plugins have migrated onto the new interface (targeting roughly three months out).

## Considered Options

### Where the plugin's code runs

A real, versioned Python package, installed into the customer's own image, was the expected direction from the start - see "Loading the python packages inside portal core" below for how the portal actually discovers one.

### Loading the python packages inside portal core

#### Option 1 (chosen): Discover plugins automatically via Python entry points
- Python's standard entry-points mechanism - the same one Airflow's own classic plugin registration uses for operators, hooks, executors, and UI views. (Airflow separately uses `pluggy`'s hookspec/hookimpl system for its listener API, where many plugins can each optionally implement several lifecycle hooks - a different shape of problem than one class per plugin, so not a reason to pull `pluggy` in here.)
- Installing the package is enough - nothing extra to configure.
- Robust and well-established: this is what "advertise yourself as a plugin" means in the Python packaging ecosystem.

#### Option 2: No automatic discovery, hardcode it through settings
- Easy to understand - one setting lists exactly what's loaded.
- More manual bookkeeping: installing a plugin isn't enough by itself, it also has to be named.
- Doesn't fit "just install it and it works."

### Where and how is the configuration of the plugin stored

A plugin's identity - its name, icon, and fields - lives directly on its own Python class, inherited from the portal's `TechnicalAssetPlugin` ABC (see Decision Outcome), alongside the configuration behavior described below; it isn't a separate thing to store.

#### Option 1: Single table for all plugins with a JSON column
- Needs a stored version per row, and some tooling to reload against it.
- Hard for migrations: a plugin author who changes a field has no real migration to write - either the portal builds a way to make that easier, or it's on the plugin author to deal with it defensively, in their own code.
- A lot of that defensiveness falls on plugin developers, since old, stored values don't automatically match a newer field declaration.
- Keeps the number of tables small - the fixed identity fields of every plugin type live in one shared table.
- Harder to index or join against, since the configured values themselves sit inside a JSON blob.

#### Option 2 (chosen): Separate table for each plugin, plus one table tracking versions
Creating a table for each plugin - the schema can be partially defined by portal core (an id, a name, a version, ...) and partially self-defined by the plugin. This stays a single table per plugin, not a denormalized model.
Included is also some basic tooling to test out Alembic database migrations of the plugin's own tables, since plugin authors should be able to try out their own migrations before shipping them, the same as they would for portal core's own.
Alongside that, one shared table tracks each plugin's table, its version, and its schema. Only the latest version needs to be kept there - older versions live in the plugin's own migration history, not in this tracking table.

- Comes with a built-in versioning system via Alembic - and this isn't custom machinery: Alembic already supports running multiple, independent migration histories side by side ("Run Multiple Alembic Environments" in its own docs), each with its own version-tracking table.
- Easier to put indexes, joins and constraints in place than against a JSON column.
- Lots of new tables, growing with however many plugins are installed.

The core project's own migrations already run as a deploy-time step, before the app starts serving traffic. That same step extends to also walk every named plugin: a plugin author writes its Alembic revisions in a `versions/` folder next to the plugin's own class (nothing declared on the class itself); the portal core discovers that folder from the class's own location and always reconciles the plugin's table to the latest revision found there.

### UI rendering of a plugin's fields and form

#### Option 1 (chosen): A plugin returns `UIElementMetadata` instances directly
- Same class already used to render every technical asset type's form, imported from the new package (see "Distributing portal core as an installable Python package" below) - nothing new to design.
- No adapter step: a plugin author gets exactly the same building block core types use, which is far less work than hand-writing a JSON schema.
- Core's own technical asset types are expected to converge onto this same interface too, so there ends up being one single, working way to declare a technical asset's form, not two.

### Distributing portal core as an installable Python package

To use environments, platforms, and platform services, and to inherit `TechnicalAssetPlugin`, a plugin needs portal core available as an ordinary Python dependency.

For a first version this exposes portal core broadly (all its classes), rather than a curated subset. Working out exactly which subset a plugin actually needs is real design work in its own right, and premature before real plugins exist on this interface - see "Out of scope". `TechnicalAssetPlugin` lives in this package, not in the existing `sdk` package: `sdk` is the thin, generated OpenAPI client, and portal core's own backend is not allowed to depend on it (a plugin class needs to be importable and inspectable from backend code, e.g. at entry-point discovery time, so the reverse dependency doesn't work). This also settles the migration path for the current, in-tree plugins: moving them out of tree means installing this same package, so the portal ends up depending on its own published artifact - eating its own dog food, gradually, one plugin per PR rather than a big-bang cutover.

Technically, this reuses the path the `sdk` package already publishes through: a Poetry-built package, published to PyPI via the `publish-sdk` job in `.github/workflows/release-workflow.yml` (using `pypa/gh-action-pypi-publish`) on every release. This decision adds a sibling package and a sibling publish job to that same workflow, rather than build new release plumbing.

## Decision Outcome
- Where the plugin's code runs: an installable Python package.
- Loading the python packages inside portal core: Option 1 - automatic discovery via Python entry points.
- The shape a plugin's class must implement: an ABC, `TechnicalAssetPlugin`, that a plugin class inherits from.
- Where and how is the configuration of the plugin stored: Option 2 - a dedicated table per plugin, migrated by the plugin's own Alembic revisions.
- Distributing portal core as an installable Python package: portal core is published to PyPI as its own package, all of it for now. `TechnicalAssetPlugin` lives here, alongside whatever a plugin needs to read environments, platforms, and platform services.
- UI rendering of a plugin's fields and form: Option 1 - a plugin returns `UIElementMetadata` instances directly, the exact class and rendering path every technical asset type already uses. Built-in types are expected to converge onto this same interface too, so there ends up being one single way to declare a technical asset's form, not a plugin-specific one.
- The current, in-tree plugins also move onto this interface, not just future third-party ones - gradually, one plugin per PR, so the portal eats its own dog food.

### Confirmation

This decision is reflected in the application by:

* A new integration is added by installing it as a package into the customer's own image, with no change to the core project and no fork of it - discovered automatically via its entry point, no separate naming step required.
* A plugin's own identity lives directly on its Python class, right alongside its code - the icon is a bundled file path. The portal defines this shape as `TechnicalAssetPlugin`, an ABC in portal core's new installable package (see "Distributing portal core as an installable Python package"). Plugin developers get everything they need from that one package - the ABC plus read access to environments, platforms, and platform services - rather than piecing it together from multiple sources.
* Existing, in-tree plugins are packaged and installed the same way as any third-party plugin, moved out one at a time, not all at once.
* A technical asset's specific, filled-in values live in a table that belongs to that plugin, migrated by the plugin's own Alembic revisions; a shared table tracks which revision each plugin's table is currently at, and `python -m app.db_tool migrate` reconciles both core and plugin tables to the latest revision in the same existing deploy step. Plugin authors get the same basic tooling to try out their own migrations before shipping them as they would for portal core's own.
* The portal's published API description treats a technical asset's configuration lazily, and as a generic value for every type; anything needing a type's exact fields looks them up separately, at the moment it needs them.
* The API regarding technical assets is not different for dynamically loaded plugins and is read through the same `/v2/data_products/{data_product_id}/technical_assets` endpoints every built-in type already uses, not a separate, plugin-only API - so there is exactly one way to create or read a technical asset in every generated SDK/CLI/frontend client, regardless of which system backs it.
* A plugin declares its fields as `UIElementMetadata` instances directly (see "UI rendering of a plugin's fields and form") - the same class and rendering path every technical asset type already uses to describe its form. A plugin author never writes frontend code and never hand-writes JSON for its form; it returns the objects, and the portal renders them.
* Existing integrations move onto the new interface one at a time; both the old, table-per-type mechanism and the new, plugin-owned-table mechanism are supported until the last one moves.

## Design Details

Lower-level implementation choices that follow from the decision above, but aren't themselves a separate option that was weighed:

* Running a customer's own plugin code safely is that customer's own responsibility; the portal does not add sandboxing, code review, or resource limits as part of this decision.
* Calls into a plugin's code are wrapped by the portal at the call boundary: an uncaught exception is caught, logged with its stack trace, and surfaced as a clean error, so one broken plugin can't take down the request it's handling.
* Alongside its own `values`, a plugin's methods are passed a context object carrying whatever's generic across every technical asset type (its own id/name, its output port, its data product, its domain).
* If a plugin's own validation is backed by a dynamically-built model (e.g. Pydantic) for nicer error messages, that model stays internal to `validate` - it never becomes part of the generated OpenAPI schema, SDK, or CLI types.

## Pros and Cons of the Options

### Loading the python packages inside portal core - Option 1 (chosen): automatic, via entry points
- **Good, because** installing the package is enough - nothing extra to configure or forget.
- **Good, because** it's a standard, well-understood Python mechanism, not something built from scratch.
- **Bad, because** anything already installed - including a dependency nobody chose on purpose - could advertise itself the same way and get loaded; what's running is only visible in the dependency tree, not the Dockerfile. Mitigated by having the portal log every discovered plugin at startup, so what's actually loaded is always visible at runtime.

### Loading the python packages inside portal core - Option 2: explicit naming through settings
- **Good, because** nothing loads that wasn't named on purpose - reviewable in one setting.
- **Bad, because** it doubles the bookkeeping: install and name are two separate steps, and forgetting the second fails silently.

### Where and how is the configuration of the plugin stored - Option 1: single JSON column
- **Good, because** no migration is ever needed to add or change an integration.
- **Bad, because** validating at save time doesn't help with rows already saved under an older version of a plugin's fields - every plugin author defensively guesses at a shape they can't fully trust.
- **Bad, because** a plain database query against one specific field, across every technical asset using it, becomes a more roundabout query against the JSON blob instead.

### Where and how is the configuration of the plugin stored - Option 2 (chosen): dedicated table per plugin, Alembic-migrated
- **Good, because** a migration can reshape or backfill old data as part of the same change that needs it - something the JSON column can't do.
- **Good, because** it reuses the deploy-time migration step the core project already runs; no new infrastructure needed to apply it.
- **Good, because** running several independent migration histories side by side is a documented Alembic pattern, not something built from scratch.
- **Bad, because** every field change now needs a real, shipped migration, authored by the plugin - more work than editing a declared field.
- **Neutral, because** uninstalling a plugin doesn't clean up its table - it's left in place, untouched, with nothing else happening; picked up again if the plugin is reinstalled.

### UI rendering of a plugin's fields and form - Option 1 (chosen): a plugin returns `UIElementMetadata` directly
- **Good, because** nothing new to design - a plugin author reuses the exact class every technical asset type already renders with.
- **Good, because** no adapter, no translation layer to maintain.
- **Neutral, because** a plugin is coupled to `UIElementMetadata`'s own shape; the same is already true for every built-in type, and built-ins are expected to converge onto this same interface too.


## Appendix

### The alternatives for where the code can run

1. **Build it into the core project (today's situation)** - rejected, this is the exact problem being solved.
2. **Ship it as a separately installable package** - built and versioned like any other Python package, installed into the customer's own image.
   * **2a (chosen) - discovered automatically**, via Python's standard package-registration mechanism.
   * **2b - discovered by explicit name** - the image author names exactly which modules to load, in one setting.
3. **Drop it into a scanned folder, loaded in-process** - the portal imports a plugin file directly at startup, no packaging needed.
4. **Drop it into a scanned folder, run as a separate program per call** - any language, isolates a broken plugin, but slower per call and more work to build.
5. **Run it inside the portal, in a locked-down sandbox** - safe by construction, but needs a new sandboxable-format runtime.
6. **Run it entirely on a separate server the plugin author operates** - 6a renders its own screen, 6b just answers questions for the portal's generic renderer.
7. **Build a public marketplace** - a way to find plugin code; could sit on top of any option above.
