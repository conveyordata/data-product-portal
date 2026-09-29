# Output Port Access Types

## Context and Problem Statement

Output Ports have a hardcoded access level (`UNRESTRICTED`, `RESTRICTED`, `PRIVATE`) that is both the label users see and the
behaviour Portal enforces. Customers often want their own names for how Output Ports are shared (e.g. Open / Internal on request / Need to know)
and want to use those names directly. We introduce admin-defined **Access Types** that each map to one of the three fixed
**Access Functions** (see `CONTEXT.md`). The behaviour of the three functions does not change.

This raises the question of where the Access Function of an Output Port is resolved. The access level is checked on hot paths: the
ORM filter that hides private Output Ports on every SELECT (`output_ports/model.py`), the Casbin `output-port-reader` wildcard grouping,
auto-approval and approval emails. A join to an Access Type table on each of those paths was raised as a performance concern.

Read access for Data Products that consume an Invite only Output Port is out of scope here; it is implemented in #4392.

## Decision Drivers

* Existing Output Ports keep their behaviour for organisations that do not configure Access Types;
  new Output Ports require an explicit Access Type instead of defaulting to Unrestricted
* No extra join on the visibility hot paths
* API clients read the resolved Access Function as `access_type.access_function`; requests select an Access Type by `access_type_id`

## Considered Options

* **Option 1: Resolve on read** Output Ports only store `access_type_id`; every check joins to the Access Type.
* **Option 2: Resolve on write** Output Ports store `access_type_id` and keep `access_function` as the resolved Access Function,
  rewritten whenever the Access Type is set or remapped.

## Decision Outcome

**Chosen option:** *Option 2: Resolve on write*. It leaves every existing branch on `access_function` untouched and adds no join to the access checks.
Loading the Access Type to display its name is a join on a primary key into a small table and is acceptable; only the
access checks must avoid it.
Remapping an Access Type is a rare admin action, so paying for it there (updating the affected ports and resyncing their Casbin
reader grouping) is cheap.

We call the admin-defined entries **Access Types** rather than Classifications, because "Classification" suggests data-sensitivity
labelling, while these entries only decide who can see and access an Output Port.

### Confirmation

* An `output_port_access_types` table holds name, description and Access Function (`access_function`). It is seeded with Unrestricted,
  Restricted and Private, mapped 1:1.
* `datasets.access_type_id` is backfilled from the former `access_type` enum column, which stays on the port as the
  resolved Access Function and is renamed to `access_function`. `access_type_id` then becomes required.
* This is a breaking API change. Output Port create and update requests require `access_type_id` and no longer accept
  the `access_type` enum. Responses return `access_type` as an object with its `id`, `name` and `access_function` instead of the
  former enum string.
  Clients look up the Access Type id with `GET /api/v2/configuration/output_port_access_types`
  (see `demo/agents/setup/create_products.py`).
* Remapping an Access Type updates `access_function` on its Output Ports and re-runs `_sync_public_reader_grouping` for each of them.
  A remap that moves an Access Type in use under a Hidden Data Product out of Invite only is refused.
* An Access Type in use cannot be deleted. The last Access Type mapped to Invite only cannot be deleted or remapped, so
  Hidden Data Products can always create Output Ports.

## Pros and Cons of the Options

### Option 1: Resolve on read

* **Good, because** a remap takes effect without rewriting Output Ports.
* **Bad, because** it adds a join to the ORM filter that runs on every Output Port SELECT, including relationship loads.
* **Bad, because** the Casbin reader grouping is materialised per Output Port anyway, so a remap still needs a resync.

### Option 2: Resolve on write

* **Good, because** all current checks on `access_function` keep working unchanged.
* **Good, because** hot paths stay as fast as today.
* **Bad, because** `access_function` is derived data that must be rewritten on every Access Type change.
