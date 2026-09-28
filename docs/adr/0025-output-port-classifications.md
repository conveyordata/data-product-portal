# Output Port Classifications

## Context and Problem Statement

Output Ports have a hardcoded access type (`UNRESTRICTED`, `RESTRICTED`, `PRIVATE`) that is both the label users see and the
behaviour Portal enforces. Customers often run their own classification schemes (e.g. Public / Internal / Confidential / Secret)
and want to use those names directly. We introduce admin-defined **Classifications** that each map to one of the three fixed
**Access Functions** (see `CONTEXT.md`). The behaviour of the three functions does not change.

This raises the question of where the Access Function of an Output Port is resolved. The access type is checked on hot paths: the
ORM filter that hides private Output Ports on every SELECT (`output_ports/model.py`), the Casbin `output-port-reader` wildcard grouping,
auto-approval and approval emails. A join to a Classification table on each of those paths was raised as a performance concern.

Read access for Data Products that consume an Invite only Output Port is out of scope here; it is implemented in #4392.

## Decision Drivers

* No behaviour change for organisations that do not configure Classifications
* No extra join on the visibility hot paths
* API clients read the resolved Access Function as `classification.access_type`; requests select a Classification by `classification_id`

## Considered Options

* **Option 1: Resolve on read** Output Ports only store `classification_id`; every check joins to the Classification.
* **Option 2: Resolve on write** Output Ports store `classification_id` and keep `access_type` as the resolved Access Function,
  rewritten whenever the Classification is set or remapped.

## Decision Outcome

**Chosen option:** *Option 2: Resolve on write*. It leaves every existing branch on `access_type` untouched and adds no join to the access checks.
Loading the Classification to display its name is a join on a primary key into a small table and is acceptable; only the
access checks must avoid it.
Remapping a Classification is a rare admin action, so paying for it there (updating the affected ports and resyncing their Casbin
reader grouping) is cheap.

### Confirmation

* A `output_port_classifications` table holds name, description and Access Function. It is seeded with Unrestricted,
  Restricted and Private, mapped 1:1.
* `datasets.classification_id` is backfilled from `access_type` and becomes required. `access_type` stays on the port as the
  resolved Access Function.
* This is a breaking API change. Output Port create and update requests require `classification_id` and no longer accept
  `access_type`. Responses embed `classification` with its `id`, `name` and `access_type`, and drop the top-level `access_type`.
  Clients look up the Classification id with `GET /api/v2/configuration/output_port_classifications`
  (see `demo/agents/setup/create_products.py`).
* Remapping a Classification updates `access_type` on its Output Ports and re-runs `_sync_public_reader_grouping` for each of them.
  A remap that moves a Classification in use under a Hidden Data Product out of Invite only is refused.
* A Classification in use cannot be deleted. The last Classification mapped to Invite only cannot be deleted or remapped, so
  Hidden Data Products can always create Output Ports.

## Pros and Cons of the Options

### Option 1: Resolve on read

* **Good, because** a remap takes effect without rewriting Output Ports.
* **Bad, because** it adds a join to the ORM filter that runs on every Output Port SELECT, including relationship loads.
* **Bad, because** the Casbin reader grouping is materialised per Output Port anyway, so a remap still needs a resync.

### Option 2: Resolve on write

* **Good, because** all current checks on `access_type` keep working unchanged.
* **Good, because** hot paths stay as fast as today.
* **Bad, because** `access_type` is derived data that must be rewritten on every Classification change.
