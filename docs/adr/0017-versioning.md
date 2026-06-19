# Output Port Versioning

## Context and Problem Statement

Producers need to evolve their data products over time. When a Producer changes a table schema or data transformation logic, Consumers currently have no control over when they adopt the change. The Portal has no built-in versioning, so schema changes are immediately visible to all Consumers, potentially breaking their pipelines.

The current workaround is to manually create new Technical Assets and Output Ports for each version, which shows duplicates in the marketplace and forces Consumers to re-request access from scratch.

**Core question: How should Output Port versioning work?**

This ADR focuses on the versioning mechanism itself. Notification UX, deprecation workflows, and detailed authorization rules are separate concerns.

## Decision Drivers

* Consumer protection: downstream pipelines must not be broken by breaking schema changes they didn't opt into
* Operational realism: Producers shouldn't be burdened with maintaining many parallel versions
* Platform flexibility: Must work whether the Technical Asset is a table, a schema, an S3 bucket, or a Kafka topic
* Consumer visibility: Consumers should know when something changes, even if it's backward-compatible or non-breaking
* Access continuity: Versioning should not force Consumers through the access request flow again. At least not in the first version

## Considered Options

* **Option 1: No versioning** - Producers update Technical Assets in place; Consumers always see latest
* **Option 2: Major-only versioning** - New Output Port only for breaking changes; non-breaking changes update in place silently
* **Option 3: Semantic versioning with major-only branching** - Use semver to track all changes; only major versions create new Output Port records; minor/patch are metadata updates on the existing Output Port
* **Option 4: Full versioning** - Every change (major/minor/patch) creates a new Output Port + new Technical Asset

## Decision Outcome

**Chosen option: Option 3 - Semantic versioning with major-only branching.Or Option 2 - Only major versions as an MVP first**

Use semantic versioning (major.minor.patch) to track all changes to an Output Port. Only **major version bumps** (breaking changes) create a new Output Port record and link a new TA to it. Minor and patch bumps are metadata updates (version field + changelog entry + notification) on the existing Output Port, downstream Consumers can only specify a major version, patch and minor are always at latest automatically. e.g. v2.x.x

**Rationale:**

Think of each major version as a long-lived **branch**:
- **v1** starts at 1.0.0, evolves through 1.1.0, 1.2.0, etc. - all in-place on the same Output Port record.
- **v2** is created when a breaking change is necessary. It starts at 2.0.0 and evolves independently.
- v1 and v2 coexist until v1 is deprecated.

This gives both change tracking (via semver) and operational realism (infra duplication only when needed).

### Why semver?

Data pipelines have CI/CD release cycles just like regular software. A dbt project is committed, reviewed, and deployed. Each deployment that changes the schema IS a release. The distinction is: version on **code deploy** (schema change), not on every pipeline **run** (data refresh). This is no different from an API that versions on deploy, not on every request.

### Why only branch on major?

A minor version (adding a column) is backward-compatible by definition - the Consumer already has access to the new data. Creating separate infrastructure for each minor version leads to operational sprawl (maintaining v1.0, v1.1, v1.2, v1.3 views all pointing to the same underlying table). What Consumers need for minor changes is **notification**, not a separate version with its own Technical Asset.

### How it works

**Patch changes** (1.0.0 → 1.0.1):
- Data quality fixes, documentation updates, performance improvements
- Update in place, bump version number on existing Output Port
- Notify Consumers via changelog

**Minor changes** (1.0.0 → 1.1.0):
- Backward-compatible additions (new column, new file, new API field)
- Update in place, bump version number on existing Output Port
- Notify Consumers via changelog
- deprecations, warn users of fields that will be removed in a new version, and give them an alternative in the changelog

**Breaking changes** (1.x.x → 2.0.0):
- Producer creates new Output Port version (v2) with new Technical Asset (or existing one in case of schemas)
- Examples: Removing columns, renaming columns, changing data types, schema restructuring
- Consumers on v1 continue using old infrastructure
- Access to v2 is **automatically inherited** — no re-requesting
- Consumers confirm when they're ready to switch; only after can the v1 be removed.
- Both versions coexist during migration period

**When to version:** Only when the change would break existing Consumer queries or code.

**Key principle:** Versions are long-lived branches, not frequent releases. A data product might have only 2-3 major versions over its lifetime.

### Access inheritance for major versions

When a Producer creates v2 of an Output Port, all Consumers with an input port on v1 automatically receive access to v2. They don't need to go through the access request flow again - requiring re-requests would recreate the exact problem we're solving today.

Consumers confirm when they've updated their code to use v2. Until they confirm, their input port on v1 remains active.

### The schema-level Technical Asset case (dbt)

In some setups the Technical Asset is a **database schema** (e.g., `gold.marketing`), not an individual table. Access is granted at the schema level. When a Producer uses dbt model versioning, `customers_v2` appears in the **same schema** as `customers`.

In this case:
- The Technical Asset (schema) doesn't change between Output Port versions
- v1 says "use `customers`"; v2 says "use `customers_v2`" - both within the same schema
- Versioning here is about **communication** (the contract), not access control
- No need to create new Technical Assets for every breaking table change in a schema with dozens of tables

The Portal supports this by allowing multiple Output Port versions to reference the **same** Technical Asset. The version contract (documentation, data contract) tells Consumers which tables/views correspond to their version.

For setups where the Technical Asset is an individual table, a new major version will typically reference a new Technical Asset. The model supports both cases.

### Confirmation

- Output Ports use semantic versioning (major.minor.patch), stored as a string
- Patch/minor bumps update the `version` field on the existing Output Port record + add a changelog entry + trigger notification
- Major bumps create a **new** Output Port record with `parent_version_id` pointing to the previous version
- New major versions can reference the same or different Technical Assets (platform-dependent)
- All active input ports have access to all versions. They are not copied explicitly
- Both versions coexist until the old version is explicitly deprecated
- Changelog tracks all changes (major, minor, and patch)

## Pros and Cons of the Options

### Option 1: No versioning

* **Good, because** simplest possible solution - no new infrastructure needed
* **Good, because** matches how most internal databases work today
* **Bad, because** Producers can't make breaking changes without breaking Consumers
* **Bad, because** forces workaround of creating separate Output ports and technical assets for v1/v2
* **Bad, because** versioning is not managed by portal and multiple versions show up as duplicates in the marketplace
* **Bad, because** Access request flow is duplicated

### Option 2: Major-only versioning (no change tracking)

* **Good, because** operationally realistic - only creates new Output Port when necessary
* **Good, because** clear rule: version on breaking change, update in-place otherwise
* **Good, because** aligns with how databases evolve (backward-compatible schema additions are normal)
* **Neutral, because** requires Producers to understand what "breaking" means for their Consumers
* **Bad, because** backward-compatible changes happen silently — Consumers have no visibility into what changed or when

### Option 3: Semantic versioning with major-only branching

* **Good, because** uses semver, which is familiar and well-understood across software and data engineering
* **Good, because** all changes are tracked and communicated (minor/patch via changelog + notification)
* **Good, because** only branches on major versions — no infrastructure sprawl for backward-compatible changes
* **Good, because** works for both table-level and schema-level Technical Assets
* **Good, because** access is inherited — Consumers don't repeat the access request flow on breaking changes
* **Good, because** integrates naturally with CI/CD (bump version on deploy)
* **Neutral, because** requires Producers to understand what "breaking" means
* **Bad, because** more moving parts than Option 2 (semver tracking, changelog, notifications)

### Option 4: Full versioning (all changes create new versions)

* **Good, because** maximum Consumer control - every change is opt-in
* **Good, because** clean separation - each version is completely independent
* **Bad, because** operationally unsustainable - would require maintaining dozens of views/endpoints
* **Bad, because** doesn't match how databases actually evolve
* **Bad, because** creates massive infrastructure overhead
* **Bad, because** unclear when to version (is adding an index a new version?)

---

## Design Details

### What constitutes a breaking change?

Changes that would cause existing Consumer queries or code to fail:

**Breaking (requires new version):**
- Removing a column
- Renaming a column
- Changing a column's data type
- Removing an API endpoint
- Changing API response structure
- Restructuring file formats
- Removing required fields
- Changing data freshness (e.g., real-time → daily batch)

**Not breaking (update in-place):**
- Adding a new column
- Changing column order
- Adding a new API endpoint
- Adding fields to JSON
- Adding new files to S3 prefix
- Performance improvements
- Data quality fixes
- Documentation updates

---

## Open Questions

1. **How long should old versions be supported?**
   - No technical enforcement - purely a governance/SLA question
   - Recommendation: Set deprecation timeline when making a new major version bump (e.g., 6 months notice)
   - Portal can track which Consumers are on which version to inform deprecation

2. **What about data contracts?**
   - If data contracts are adopted, they could help identify breaking changes
   - Contract diff tool could flag schema changes as breaking/non-breaking
   - This is complementary to versioning, not a replacement. Major versions have different contracts
   - See: ADR-0012 (Bitol standard supports data contracts)

4. **Should there be a "latest" alias?**
   - We will not support aliases

5. **How does this interact with data quality issues?**
   - If v1 has bad data and it's fixed, all v1 Consumers see the fix automatically
   - This is a patch bump (1.0.0 → 1.0.1) with a changelog entry
   - Consumers are notified via changelog; no migration required
   - Quality should be posted per major version that is live
