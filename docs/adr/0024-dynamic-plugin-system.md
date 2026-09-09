# Dynamically Loadable Plugin System

**Status:** Proposed - draft for iteration, not yet accepted.

## Context and Problem Statement

The portal already lets data products connect to external platforms (S3, Snowflake, Postgres, Databricks, and others) through a plugin mechanism. Today, adding a brand-new one of these means: writing new code, creating a brand-new database table just for that one integration, writing a database migration to create that table, and editing a couple of internal registration lists - all inside the core project. Because all of that lives in the core project, adding an integration always means submitting a change to it (or forking it).

A second, less visible problem sits underneath that. Each integration's basic identity - its name, its icon, which vendor it belongs to, and what fields it needs - is currently written down **twice**: once in the code that implements it, and once as rows that have to be separately created in the database. Nothing keeps these two copies in sync automatically; they only agree because whoever set both of them up happened to spell everything identically. When they don't match exactly, the integration's tile still shows up in the interface, but trying to actually use it fails, without a clear reason why.

A third, related problem is how the portal stores per-environment infrastructure details (which storage buckets exist in "dev" vs. "production", which credentials apply where). This information is currently spread across several separate database tables that have grown into a genuinely complicated arrangement, with some facts (like a shared account identifier) effectively repeated across places that are hard to keep in sync with each other.

One concrete request is driving this redesign: a customer needs to add their own custom integration without submitting a change to the core project and without forking it.

**Core question: how should a plugin's code run, and how should a plugin's information be modeled and stored, so that adding one never requires a database migration and never requires a change to the core project - including for an integration that needs to remember real, structured settings?**

## Decision Drivers

* Adding or changing an integration should never require a database migration - including one that needs real, persisted settings.
* Adding an integration should never require submitting a change to the core project, or maintaining a fork of it.
* Whatever a plugin author has to do to add an integration should be as light as reasonably possible - dropping something into a folder is preferable to having to build and run a separate always-on service.
* Keep what already works well: form fields are already generated generically from whatever fields an integration declares, and the human-readable summary text shown to users is already filled in generically using those same fields, by name. Any redesign should build on this, not throw it away.
* Where today's way of storing an integration's identity and its environment-specific configuration is itself the cause of duplication or confusion, it is fair to change it - but a full, unrelated rename or redesign of every related concept is not the goal here.
* Whatever is decided needs a realistic, low-disruption way to move the handful of integrations that already exist onto it, rather than leaving them permanently on a separate, older system.
* Simplicity beats defensiveness: given every customer runs their own separate, self-hosted copy of the portal, prefer the simplest option that works over one that defends against risks that don't apply to this deployment model.
* What gets loaded into the running portal should always be something an image author named on purpose - never something that got in automatically because it happened to be installed.

## Considered Options

### Where the plugin's code runs

#### Option 1: Build it into the core project (today's situation)
Rejected - this is the exact problem being solved.

#### Option 2: Ship it as a separately installable package
A real, versioned package (built the same way as any other Python package here), installed into the customer's own image. No fork needed, but it still means rebuilding and redeploying the customer's own copy every time. Two ways the portal could learn it's there:

* **2a - discovered automatically**, the way Python packages can advertise themselves through a standard registration mechanism. Costs nothing to set up, but it's a real predictability problem: anything already installed - including some dependency of a dependency, never chosen on purpose - could advertise itself the same way and get loaded into the running portal, with nothing in the Dockerfile naming it.
* **2b - discovered by explicit name**: the image author writes down, in one setting, exactly which packages/modules to load. Nothing loads that wasn't named on purpose. Costs one extra line to maintain, and it's possible to forget to add it after installing the package, which fails quietly (the package is present, but never loaded) rather than loudly.

#### Option 3: Drop it into a scanned folder, loaded in-process
The portal scans a folder on startup and loads a plugin's file directly into its own running program. Simple, but it gives up two things a real package would have: nowhere to declare the plugin's own dependencies (a customer has to install those by hand, disconnected from the plugin that needs them), and no version to pin or roll back - rolling one back means restoring the right files, not changing a number.

#### Option 4: Drop it into a scanned folder, run as a separate program per call
Instead of loading the dropped-in file into its own program, the portal treats it as its own small, separate program, and runs a fresh copy of it each time it needs something, exchanging only plain, simple information back and forth. This allows a plugin to be written in any language at all, and a mistake in one plugin can't directly corrupt the portal's own running program the way it could with Option 3.
The trade-off: starting a fresh small program for every single request is somewhat slower and more work to build, and it still offers no protection against code that is deliberately malicious, only against accidental interference. This idea fits a folder of loose files; it doesn't naturally extend to an installed package that gets imported by name (Option 2), since there the whole point is that Python already loads it directly.

#### Option 5: Run it inside the portal, but in a locked-down sandbox
Cannot touch the filesystem, network, or database unless explicitly allowed to. This means a plugin author never has to run their own server, while genuinely bad code still cannot cause real damage. The real cost: a plugin has to be written in, or compiled into, a specific portable, sandboxable format, and the portal needs new infrastructure able to run that format - a real, non-trivial addition.

#### Option 6: Run it entirely on a separate server the plugin author operates
The portal only ever sends it requests over the network. Two flavors: **6a**, where that server also decides exactly what the screen looks like (a fully custom mini-screen embedded into the page); or **6b**, where that server only answers questions, and the screen itself stays a plain description of fields and labels that the portal renders the same generic way it already does today.

#### Option 7: Build a public marketplace
Let people browse and install plugins written by others, with some form of review before something gets listed. It's a way of finding plugin code, and it could sit on top of any of the options above.

### Where is the basic metadata of the plugin stored

This is the basic identity of an integration: its name, its icon, and the list of fields it needs.
Today, this is defined twice - once by the plugin's own code, and once by rows that must be separately, manually created in the database, kept in sync only by both sides spelling everything identically.

#### Option 1:  Portal code as well as database row (as today)
Rejected - this is the exact duplication problem being fixed.

#### Option 2: Only keep the database row.
These filled in by an admin through a form or an API call, with no matching copy of that information anywhere in a plugin's own code.

#### Option 3: Store externally and import at runtime
It carries a small, plain description of its own name, icon, and fields, sitting right alongside its own code.
The portal reads this description at the same moment it discovers the plugin's code, and that description is the *only* place this information exists - nobody has to separately re-type it anywhere. An extension or plugin ships its own description together with its own code, instead of a separate person entering the same facts into a form by hand.

### Where a technical asset's configured values are stored

This is about the values one data product fills in for its use of an integration, separate from whether the integration itself exists.
Today, every single integration type gets its own dedicated table in the database purely to hold this, as a result adding one requires a database migration.

#### Option 1: Keep a dedicated table per integration type
As today is the case. Precise, and easy to query directly, but a migration is required every single time.

#### Option 2: Use one shared, flexible column that can hold any integration's filled-in values
This can be checked for correctness against that integration's own declared fields at the moment it's saved, rather than being enforced by the shape of a database table.
No migration is ever needed to add a new integration. The one thing it does give up is the ability to write a plain, simple database query like "show me every technical asset using a particular value" directly against a fixed column - that becomes a slightly more roundabout query against the flexible column instead, and nothing today actually does this.

### Where per-environment infrastructure details are stored

Take S3, used in three environments: dev, staging, production. The following tables hold facts about this today:

1. **`env_platform_configs`** - a shared table. For "dev", it holds the AWS account number and region. Every AWS service in dev reads these same values, not just S3.
2. **`env_platform_service_configs`** - an S3-only table (one row set per service). For "dev", it holds the real bucket names, ARNs, and encryption keys. Only S3 reads its own rows here.
3. **`platform_service_configs`** - a separate table with no environment at all. It just lists valid names like `datalake`, `ingress`, `egress`. It fills a dropdown.

Creating an S3 asset in "dev" reads from all three: account and region from `env_platform_configs`, real bucket details from `env_platform_service_configs`, and the name must also appear in `platform_service_configs`.

#### Option 1: Merge `env_platform_configs` and `env_platform_service_configs`
One row per environment per integration. "S3 in dev" holds the account, region, and bucket list together. Cost: if Glue also runs in dev, "Glue in dev" needs its own copy of that same account and region.

#### Option 2: Reuse the mechanism from the technical-asset-values decision
When someone creates an S3 asset, they fill in a form. The portal checks it against S3's fields. That's one filled-in, checked record, tied to one asset. Setting up "dev" for S3 works the same way: fill in a form, check it against the same fields. The only difference is that the record is tied to an environment instead of an asset, and a platform engineer fills it in instead of a data product owner. Store both the same way instead of building two separate systems.

#### Option 3: Drop `platform_service_configs`
It only says "`datalake` is a valid name." That's already true if any real row in `env_platform_service_configs` uses that name. Read the list from there instead. Delete `platform_service_configs`.

#### Option 4: Let each plugin own its own environment-config shape
Delete all three tables. Replace them with one generic table: one record per plugin per environment, holding a checked blob of values, with a single shape per plugin instead of a separate vendor-level and service-level split.

The plugin's own file - the same file that already declares its name, icon, and fields - also declares the shape it needs per environment. For S3, that might be an account ID, a region, and a list of buckets. A company with five AWS accounts writes a different shape into their own S3 plugin instead - a list of accounts, say. The portal never fixes one shape for "what a cloud platform looks like"; it just renders a form from whatever shape the plugin declares, and stores whatever comes back, the same way it already does for a technical asset's own values.

Cost: today, a shared account and region can be filled in once for "dev" and read by every AWS plugin, through `env_platform_configs`. With this option, that sharing goes away - S3 and Glue each fill in their own account number for "dev," since there's no shared, portal-level place left to read it from. If two plugins genuinely need to share a fact, that becomes the plugin author's problem to solve (for instance, writing one plugin that covers both services), not something the portal provides automatically. The "valid names" idea survives in a smaller form too: a plugin that wants a dropdown of names derives it from its own environment records only, not shared across plugins from the same vendor.

### How the API describes a plugin's configuration

The portal publishes a machine-readable description of its API, and a frontend client, a Python SDK, and a Go CLI are all generated from it. Once a technical asset's configuration is one flexible, checked value instead of fixed columns per type, that description has a choice to make.

#### Option 1: Describe every loaded type in full
List the exact fields of every plugin currently loaded, built-in and custom alike, so a generated client sees each type's real shape. Problem: the description would then differ from one deployment to the next, depending on which plugins happen to be installed there, and a tool that checks types before the program even runs cannot check something whose shape is only known once the program is running.

#### Option 2: Describe it as a generic value, for every type
The description says a technical asset's configuration is "some object," the same way for every plugin, built-in or custom. Real checking still happens the moment something is saved - nothing gets less validated - but the generated client's types no longer show a plugin's exact fields ahead of time. Whoever needs those fields (to build a form, say) asks for them separately, through a plain lookup, at the moment they need them.

#### Option 3: A mix - full detail for built-in types, generic for custom ones
Keeps built-in types precisely described and only custom ones generic. Splits every asset type into two classes with different guarantees, and still leaves the underlying problem - some types are only known once the program runs - half-solved rather than avoided.

### How existing plugins move onto the new system

#### Option 1: Move everything over in one coordinated piece of work
Every existing plugin's stored values are copied, once, from its current dedicated table into the new flexible column. Every existing plugin's code is rewritten against the new interface at the same time. Done together, in one release.

#### Option 2: Run both systems side by side for a transition period
Old, table-per-type plugins and new, flexible-column plugins coexist for a while, and plugins move over one at a time. Every piece of generic code that touches a technical asset's configuration (rendering a result, validating a form, exposing it through the API) has to handle both shapes until the last old plugin is moved, which reintroduces, temporarily, the exact kind of duplicated, parallel logic this whole change exists to remove.

## Decision Outcome

**Chosen options:**
* Where the plugin's code runs: **Option 2b** - ship it as an installable package, discovered by explicitly naming which modules to load.
* Where the plugin's metadata is stored: **Option 3** - store it externally and import it at runtime, alongside its own code.
* Where a technical asset's configured values are stored: **Option 2** - one shared, flexible column.
* Where per-environment infrastructure details are stored: **Option 4** - let each plugin own its own environment-config shape.
* How the API describes a plugin's configuration: **Option 2** - a generic value, for every type.
* How existing plugins move onto the new system: **Option 1** - one coordinated cutover.

Both integrations that "come with the portal" and integrations a customer writes themselves are installed and discovered exactly the same way - one bundled into the published image, one added by the customer's own Dockerfile - so the two are naturally treated as equals, not as two separate systems bolted together.

Option 2b is chosen over 2a (automatic discovery) because automatic discovery is a real predictability problem, not just a convenience one: with it, anything already installed - including some dependency of a dependency, never chosen on purpose - could get loaded into the running portal without anyone naming it. Naming the exact modules to load, in one explicit setting, costs one line and keeps that decision where it belongs: with whoever wrote the Dockerfile. Option 2b is chosen over Option 3 (a raw folder of files) because a real, versioned package gives two things a folder can't: a plugin can declare its own dependencies and have them installed automatically instead of a customer hand-maintaining that step, and a plugin has a version to pin and roll back, the same way any other dependency does. Because a named module is imported directly, it runs in-process - Option 4 (running each dropped-in file as its own separate small program per call) was really an answer suited to a folder of loose files, and doesn't naturally apply once a real package is being installed and imported by name.

The same reasoning that ruled out Options 5 and 6 (sandboxed execution, and a separately operated service) still applies: those solve a shared-tenancy trust problem - protecting the portal from code written by people it doesn't control, running alongside other tenants' code - that doesn't exist here, since every customer runs their own, entirely separate, self-hosted copy of the portal. They remain documented, real alternatives, worth revisiting only if this software ever moves toward a single, shared, multi-tenant service.

Because an installed plugin's code runs with the same level of access as the portal itself, and no sandboxing is being added, the risk that code poses is treated as the customer's own responsibility, not something the portal needs to guard against. The plugin runs inside that customer's own deployment, written by that customer (or someone they've chosen to trust), touching only their own infrastructure and their own data - the same trust already implied by that customer building and running their own container image. No additional guardrails, review process, or resource limits are introduced by this decision.

Option 7 (a marketplace) is documented as a real, legitimate option, but not adopted now: that machinery exists to protect people from code written by strangers, and today there are exactly two known plugin authors, each writing an integration for their own private, self-hosted deployment - nobody unknown to vet yet. It can be added later, on top of whichever mechanism is chosen, without needing to be decided now.

Per-environment infrastructure details use Option 4, not the earlier idea of reusing one shared mechanism while still splitting vendor-wide from integration-specific facts: this extends the same self-describing choice already made for a plugin's metadata one step further, so the same file that declares a plugin's name, icon, and fields also declares the shape of its own per-environment settings. This fits any organization's structure - one AWS account or five, one region or many - since the portal never fixes one shape for "what a cloud platform looks like." The cost is accepted deliberately: a fact shared across same-vendor plugins today, like one AWS account number, is no longer read from a single shared place - each plugin asks for what it needs on its own, which means filling it in once per plugin rather than once per environment. If that turns out to matter in practice, sharing between plugins from the same vendor is something a plugin author can still design for themselves (for instance, one plugin covering several services), rather than something the portal provides automatically.

How the API describes a plugin's configuration follows directly from that same technical-asset-values decision: once a technical asset's fields aren't fixed columns per type, there's no fixed shape left for the published API description to show, for any type, built-in or custom. The description treats configuration as a generic value everywhere; a plain lookup, already used today by the portal's own interface to build its forms, is how anything that needs a type's exact fields gets them, at the moment it needs them, instead of ahead of time from generated types. The real cost, accepted here: anyone using the generated SDK or CLI today with fully typed fields for a specific asset type loses that typing, for existing types as well as new ones. A grace period around release - keeping some typed convenience for the existing types for a transition window, say - is worth considering at implementation time, but is not decided here.

Existing plugins move over in one coordinated cutover: there are only a handful of them, all known and controlled by the same team doing the work, which makes a single, well-tested pass realistic in a way it wouldn't be for a system with many independent, unknown plugin authors. Done correctly, this is not breaking for how an existing technical asset looks or behaves: its stored values move into the new shape unchanged, and the logic that renders and validates it already works by field name, not by column position, so nothing about an existing asset should visibly change. A small number of built-in plugins, S3 in particular, continue to ship with the portal after the cutover, rebuilt against the new interface - preserving today's functionality out of the box, and doubling as a working, maintained example for anyone writing their own plugin.

### Confirmation

This decision is reflected in the application by:

* A new integration is added by installing it as a package into the customer's own image and naming it explicitly in a setting, with no change to the core project and no fork of it.
* Named plugin packages are imported directly into the portal's own running program at startup.
* An integration's name, icon, and fields live in one place - right alongside its own code for integrations that have code, or as a single admin-created record for integrations that don't.
* A technical asset's specific, filled-in values are stored in one shared, flexible place, checked against the integration's declared fields, instead of each integration needing its own dedicated database table - so adding an integration never requires a database migration.
* Per-environment infrastructure details are stored as one checked, flexible record per plugin per environment, with the shape of that record declared by the plugin itself. `env_platform_configs`, `env_platform_service_configs`, and `platform_service_configs` are all removed.
* The portal's published API description treats a technical asset's configuration as a generic value for every type; anything needing a type's exact fields looks them up separately, at the moment it needs them.
* The integrations that exist today move onto this same approach in one coordinated release, not gradually - and a small number, including S3, continue to ship with the portal as working examples.
* Running a customer's own plugin code safely is that customer's own responsibility; the portal does not add sandboxing, code review, or resource limits as part of this decision.
* The plugin interface includes a hook for whether an asset type is shareable, ready for the "unshareable asset types" request to use later without needing a migration or a change to this interface.

## Interface Sketch

A plugin is one Python class, inheriting from a small base class the portal provides. The class carries both the declarative part (name, icon, the fields it needs) and the behavior part (what to actually do with those fields), together, in one place:

```python
class AssetPlugin:
    key: str                         # e.g. "s3" - the type's unique name
    display_name: str                # e.g. "S3"
    icon: str                        # inline SVG, not a bundled file
    group: str | None = None         # optional, cosmetic only - e.g. "aws"

    fields: dict                     # the fields a technical asset of this type needs
    environment_fields: dict         # the fields an environment needs to provide for this type

    def validate(self, values: dict) -> None:
        ...                           # raise if the filled-in values don't make sense together

    def render_result(self, values: dict, environment_config: dict) -> str:
        ...                           # the human-readable summary shown to a user

    def get_url(self, values: dict, environment_config: dict) -> str:
        ...                           # a link to the real resource, e.g. in the cloud provider's console

    def is_shareable(self, values: dict) -> bool:
        return True                   # default; a plugin can override this - see "Unshareable asset types"
```

`fields` and `environment_fields` are the same kind of thing described earlier under "Where is the basic metadata of the plugin stored" and "Where per-environment infrastructure details are stored" - just a plain description of what's needed. `is_shareable` is the one hook this decision adds specifically so the "unshareable asset types" request has somewhere to attach later, without needing a migration or a change to this interface when it's actually built.


Note: A plain clickable link (no environment configuration, no technical asset semantics, nothing to validate) could technically be shoehorned into this system as a plugin with an almost-empty class, just a name, an icon, and a URL template, nothing else. However it is quite heavy to use.

## Out of Scope

The following are explicitly not addressed by this decision:

* **An admin interface for managing integrations.** Integrations (including the ones with no code) remain reachable only through the underlying data/API for now, matching how they're exposed to the rest of the interface today.
* **Attaching integrations beyond data products.** Integrations continue to attach to a data product's technical assets only.

## Pros and Cons of the Options

### Where the plugin's code runs - Option 2a: installable package, discovered automatically

* **Good, because** it costs nothing extra to set up beyond installing the package.
* **Bad, because** anything already installed, including a dependency nobody chose on purpose, could advertise itself the same way and get loaded - the decision of what runs moves out of the Dockerfile and into the dependency tree.

### Where the plugin's code runs - Option 2b: installable package, discovered by explicit name

* **Good, because** it needs no change to the core project and no fork of it.
* **Good, because** it treats "comes with the portal" and "written by a customer" integrations identically.
* **Good, because** a plugin's own dependencies are declared in its own package and installed automatically, and the package carries a version that can be pinned and rolled back.
* **Good, because** nothing loads that wasn't named on purpose - a reviewable line, not an automatic side effect of installing something.
* **Neutral, because** a customer must still rebuild and redeploy their own copy of the portal to add one - accepted, since the alternative (a separately operated service) is a heavier ask.
* **Bad, because** it doubles the bookkeeping: a plugin has to be installed *and* named, and forgetting the second step gives a deployment that starts cleanly with the plugin silently absent.
* **Bad, because** an installed plugin's code has the same level of access as the portal itself - an accepted, deliberate trade-off given every customer only ever runs their own, entirely separate copy.

### Where the plugin's code runs - Option 3: drop it into a scanned folder, loaded in-process

* **Good, because** the plugin author needs no packaging knowledge - a folder of files is enough.
* **Bad, because** a plugin's own dependencies aren't declared anywhere, so a customer maintains that install step by hand.
* **Bad, because** a folder has no version - nothing to pin, and rolling back means restoring the right files rather than changing a number.

### Where the plugin's code runs - Option 4: drop it into a scanned folder, run as a separate program per call

* **Good, because** a plugin can be written in any language, and a broken plugin can't directly corrupt the portal's own running program.
* **Bad, because** it's more work to build, and slower per call, for a protection (isolating one customer's mistakes from the rest of the portal) that matters less when that customer is the only one running their own deployment anyway.

### Where the plugin's code runs - Option 5: sandboxed in-process execution

* **Good, because** a plugin author never has to run their own server, while genuinely harmful code still cannot cause damage.
* **Bad, because** it requires a plugin to be written in, or compiled into, a specific format, and requires the portal to add new infrastructure able to run that format - solving a multi-tenant safety problem this system does not currently have.

### Where the plugin's code runs - Option 6: a separate service the plugin author runs

* **Good, because** the portal never runs anyone else's code at all.
* **Bad, because** it requires every plugin author to build and keep running their own always-on service, and adds a network call (with its own failure modes) to something as simple as "open a link."

### Where the plugin's code runs - Option 7: a public marketplace

* **Good, because** it would let integrations be shared and reused across many separate customers' deployments.
* **Bad, because** the review, signing, and hosting it requires exists to protect against strangers' code, and there are currently no strangers - only two known, trusted authors, each building for their own deployment.

### Where the plugin's metadata is stored - Option 3: store it externally and import it at runtime

* **Good, because** it removes the duplicated-source-of-truth problem directly: one description, in one place, instead of two copies kept in sync by convention.
* **Neutral, because** an integration with no code at all still needs a database row created by an admin - a genuinely different case, not an inconsistency.

### Where a technical asset's configured values are stored - Option 2: one shared, flexible column

* **Good, because** it removes the need for a database migration every time an integration is added.
* **Good, because** it was checked against everything that currently touches this data, and nothing relies on fixed columns for a specific integration's own fields.
* **Bad, because** a plain, direct database query across a specific field of one integration type becomes more roundabout - accepted, since nothing today actually does this.

### Where per-environment infrastructure details are stored - Option 4: each plugin owns its own environment-config shape

* **Good, because** it fits any organization's structure - one AWS account or five, one region or many - since the portal never fixes one shape for "what a cloud platform looks like."
* **Good, because** it reuses the same self-describing mechanism already chosen for a plugin's metadata and its technical-asset values, instead of designing three separate systems.
* **Bad, because** a fact shared across same-vendor plugins today, like one AWS account, is no longer read from one shared place - each plugin asks for it separately, once per plugin instead of once per environment.
* **Bad, because** it becomes harder for an end user to tell what makes a technical asset usable at a glance, since that now depends on one specific plugin's own declared shape rather than one shared, portal-wide concept - and extending what an environment can offer for a given type is now the plugin author's own development work, not something a generic admin screen can do on its own.
* **Neutral, because** if two plugins genuinely need to share a fact, that becomes something the plugin author designs for (e.g. one plugin covering two services) rather than something the portal provides automatically.
* **Neutral, because** it still means real, one-time work to move existing environment configuration onto the new shape.

### How the API describes a plugin's configuration - Option 2: a generic value, for every type

* **Good, because** the published contract is identical across deployments - a plugin varying per deployment never makes the contract itself vary.
* **Good, because** it matches how the portal's own interface already works: fields are looked up at the moment they're needed, not baked into generated types ahead of time.
* **Neutral, because** server-side validation is unaffected - what's lost is contract fidelity in generated clients, not correctness.
* **Bad, because** it removes typed, per-field convenience from the generated SDK and CLI for every asset type, built-in ones included, not just custom ones.

### How existing plugins move onto the new system - Option 1: one coordinated cutover

* **Good, because** there are only a handful of existing plugins, all known and controlled by the same team doing the work - a realistic scope for a single, well-tested pass.
* **Good, because** it avoids the cost of maintaining two parallel plugin systems, and the duplicated logic that would require, for a transition period.
* **Good, because** keeping a small number of built-in plugins (S3, in particular) on the new interface preserves today's functionality and doubles as a working reference for anyone writing their own plugin.
* **Neutral, because** it is still real, one-time engineering work, done all at once rather than spread out.
