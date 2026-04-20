# Output Port Versioning

## Context and Problem Statement

Producers need to evolve their data products over time. When a Producer changes a table schema or data transformation logic, Consumers currently have no control over when they adopt the change. The Portal has no built-in versioning, so schema changes are immediately visible to all Consumers, potentially breaking their pipelines.

The current workaround is to manually create new technical assets and output ports for the versions, which would show duplicates in the marketplace and create confusion all around.

**Core question: Should we version Output Ports, and if so, what does a "version" represent?**

This ADR focuses narrowly on the versioning mechanism itself. Authorization, notifications, and deprecation workflows are out of scope and are subject to further ADRs.

## Decision Drivers

* Practical feasibility: Solution must be operationally realistic for Producers to maintain
* Clear versioning trigger: Must be obvious when to create a new version vs update in place
* Consumer control: Consumers need to choose when to migrate, not be forced
* Infrastructure alignment: Should work with how databases and storage actually evolve
* Minimal cognitive overhead: Producers shouldn't need to understand complex versioning rules

## Considered Options

* **Option 1: No versioning** - Producers update Technical Assets in place; Consumers always see latest
* **Option 2: Branch-based versioning** - Create new Output Port + new Technical Asset only for major versions (breaking changes)
* **Option 3: Full versioning** - Every change (major/minor/patch) creates new Output Port + new Technical Asset

## Decision Outcome

**Chosen option: Option 2 — Branch-based versioning.**

Version only when necessary: when a change would break existing Consumers. This means major version bumps only (v1 → v2 → v3).

**Rationale:**

The fundamental insight is that **data products evolve differently than software.** In software, you can have many minor versions (v1.0, v1.1, v1.2) because each represents a stable release at a point in time. In data products, there is no "release" - data flows continuously.

Trying to version every schema change creates an unsustainable operational burden. A Producer would need to maintain views for v1.0, v1.1, v1.2, v1.3, etc., all reading from the same evolving table. This doesn't match how databases actually work in practice.

Instead, think of versions as "branches":
- **v1**: The current stable version, continuously evolving with backward-compatible changes
- **v2**: A new branch created when a breaking change is necessary
- Old versions (v1) remain frozen or continue with backported fixes only

This aligns with how APIs are versioned in practice (`/api/v1/`, `/api/v2/`) and how databases are actually managed.

### How it works

**Backward-compatible changes** (no new version):
- Producer updates the Technical Asset in place
- Examples: Adding nullable columns, adding new API endpoints, new S3 files
- All Consumers on v1 automatically see the changes
- Document in changelog, but no migration required

**Breaking changes** (major version bump):
- Producer creates new Output Port (v2) with new Technical Asset
- Examples: Removing columns, renaming columns, changing data types, schema restructuring
- Consumers on v1 continue using old infrastructure
- Consumers explicitly request access to v2 when ready to migrate
- Both v1 and v2 run in parallel during migration period

**When to version:** Only when the change would break existing Consumer queries or code.

**Key principle:** Versions are long-lived branches, not frequent releases. A data product might have only 2-3 versions over its lifetime (v1, v2, maybe v3).

**Important:** Each Output Port version MUST have its own Technical Asset. You cannot have v1 and v2 pointing to the same table/bucket/API - if they did, they would return identical data and versioning would be meaningless. This means versioning always creates infrastructure duplication.

### Confirmation

- Output Ports have an optional `version` field (default: v1)
- Version is a simple integer: v1, v2, v3 (not semantic versioning)
- Creating a new version creates a new Output Port record + new Technical Asset
- Both versions coexist until the old version is explicitly deprecated
- Handshakes reference a specific Output Port version
- Backward-compatible changes are made in-place to existing versions
- Changelog tracks all changes (versioned or not)

## Pros and Cons of the Options

### Option 1: No versioning

* **Good, because** simplest possible solution - no new infrastructure needed
* **Good, because** matches how most internal databases work today
* **Good, because** no operational overhead of maintaining multiple versions
* **Bad, because** Producers can't make breaking changes without breaking Consumers
* **Bad, because** forces workaround of creating separate Output ports and technical assets for v1/v2
* **Bad, because** versioning is not managed by portal and multiple versions show up as duplicates in the marketplace

### Option 2: Branch-based versioning (major versions only)

* **Good, because** operationally realistic - only version when necessary
* **Good, because** matches how APIs are versioned in practice (v1, v2, v3)
* **Good, because** clear rule: version on breaking change, update in-place otherwise
* **Good, because** aligns with how databases evolve (backward-compatible schema additions are normal)
* **Neutral, because** requires Producers to understand what "breaking" means for their Consumers
* **Bad, because** backward-compatible changes happen without Consumer opt-in


### Option 3: Full versioning (all changes create new versions)

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

**Not breaking (update in-place):**
- Adding a new nullable column
- Adding a new API endpoint
- Adding optional fields to JSON
- Adding new files to S3 prefix
- Performance improvements
- Data quality fixes
- Documentation updates

**Gray area (Producer decides):**
- Adding a new non-nullable column (breaks `SELECT *` but not explicit column lists)
- Changing column order (breaks `SELECT *`)
- Changing data freshness (e.g., real-time → daily batch)

### Version creation flow

1. Producer determines change is breaking
2. Creates new Output Port (Portal UI or API)
   - Specify major version number (v2, v3, etc.)
   - Provide migration guide
   - Link to new Technical Asset
3. New Technical Asset is provisioned (table, view, S3 prefix, API endpoint)
4. Both versions run in parallel
5. Consumers migrate at their own pace
6. Old version is eventually deprecated and removed

### Example: Breaking change (removing a column)

**Initial state:**
- Output Port "Customer Data" v1 → Table `customers` (id, name, email, phone)

**Change needed:**
- Remove `phone` column for privacy compliance

**Steps:**
1. Create new table: `customers_v2` (id, name, email)
2. Create Output Port "Customer Data" v2 → points to `customers_v2`
3. Set up data sync from `customers` to `customers_v2` (minus phone column)
4. Consumers on v1 continue using `customers` table
5. New Consumers or migrated Consumers use v2 → `customers_v2`
6. After migration period, deprecate v1

### Example: Non-breaking change (adding a column)

**Initial state:**
- Output Port "Customer Data" v1 → Table `customers` (id, name, email)

**Change needed:**
- Add `loyalty_tier` column

**Steps:**
1. Add column to existing table: `ALTER TABLE customers ADD COLUMN loyalty_tier VARCHAR(20)`
2. Update Output Port metadata (schema documentation)
3. No new version needed - all Consumers on v1 automatically have access to new column
4. Consumers can choose to use new column or ignore it

### Database schema

```sql
-- Add version to Output Ports (datasets)
ALTER TABLE datasets ADD COLUMN version INTEGER DEFAULT 1;
ALTER TABLE datasets ADD COLUMN parent_version_id UUID REFERENCES datasets(id);

-- Add unique constraint: can't have duplicate versions for same logical port
CREATE UNIQUE INDEX idx_datasets_version
ON datasets(name, data_product_id, version);
```

No version states (active/deprecated/sunset) needed - just delete old versions when fully migrated.


## Implications and Trade-offs

### What this solves

- Producers can make breaking changes without breaking all Consumers
- Consumers have migration control for breaking changes
- Clear, simple rule: version on breaking changes only
- Operationally sustainable (2-3 versions per data product, not dozens)

### What this doesn't solve

- Consumers still auto-upgraded for non-breaking changes
- Requires Producers to correctly identify what's "breaking"
- Requires infrastructure duplication during migration periods
- No automatic rollback if a change breaks Consumers

### Comparison with software versioning

This is intentionally different from semantic versioning (major.minor.patch):

**Software versioning:**
- Many releases (v1.0.0, v1.1.0, v1.2.0, v2.0.0)
- Each release is a snapshot in time
- Clear "release" moment

**Data product versioning:**
- Few versions (v1, v2, maybe v3)
- Each version is a living thing that evolves
- No "release" - data flows continuously

Trying to apply software versioning to data products leads to operational nightmares.

---

## Open Questions

1. **What if Consumers disagree on whether a change is breaking?**
   - A Producer thinks adding a column is non-breaking (it's nullable)
   - But a Consumer using `SELECT *` will get broken code
   - Decision: Producer determines breaking-ness, but should be conservative
   - Recommendation: Producers should avoid `SELECT *` in their documentation

2. **How long should old versions be supported?**
   - No technical enforcement - purely a governance/SLA question
   - Recommendation: Set deprecation timeline per Data Product (e.g., 6 months notice)
   - Portal can track which Consumers are on which version to inform deprecation

3. **What about data contracts?**
   - If data contracts are adopted, they could help identify breaking changes
   - Contract diff tool could flag schema changes as breaking/non-breaking
   - This is complementary to versioning, not a replacement
   - See: ADR-0012 (BiToL standard supports data contracts)

4. **Should there be a "latest" alias?**
   - Deferred: Start without aliases
   - Forces Consumers to make explicit version choices
   - Can add later if there's demand for "always use latest stable"

5. **How does this interact with data quality issues?**
   - If v1 has bad data and it's fixed, all v1 Consumers see the fix
   - This is correct behavior - data quality fixes are not breaking changes
   - The data changed, but the contract (schema) didn't
