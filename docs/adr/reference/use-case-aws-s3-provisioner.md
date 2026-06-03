# Use Case: AWS S3 Platform Provisioner

This document explores what a provisioner needs to do in response to Portal events when managing an AWS S3-based data platform. Its primary purpose is to serve as input for event payload design — by working through each event, it identifies exactly what data the payload must carry for the provisioner to act without additional round-trips to the Portal.

---

## Contents

- [Platform Setup](#platform-setup)
- [Data Product Events](#data-product-events)
  - [Created](#data-product-created)
  - [Updated](#data-product-updated)
  - [Deleted](#data-product-deleted)
  - [About Updated](#data-product-about-updated)
  - [Status Updated](#data-product-status-updated)
  - [Settings Changed](#data-product-settings-changed)
  - [Team Member Added](#team-member-added)
  - [Team Member Removed](#team-member-removed)
  - [Team Member Updated](#team-member-updated-role-changed)
  - [Input Port Requested](#input-port-requested)
  - [Input Port Request Approved](#input-port-request-approved)
  - [Input Port Request Denied](#input-port-request-denied)
  - [Input Port Removed](#input-port-removed)
- [Exploration Events](#exploration-events)
  - [Created](#exploration-created)
  - [Deleted](#exploration-deleted)
  - [Input Port Requested](#exploration-input-port-requested)
  - [Input Port Request Approved](#exploration-input-port-request-approved)
  - [Input Port Request Denied](#exploration-input-port-request-denied)
  - [Input Port Removed](#exploration-input-port-removed)
- [Output Port Events](#output-port-events)
  - [Created](#output-port-created)
  - [Updated](#output-port-updated)
  - [Deleted](#output-port-deleted)
  - [About Updated](#output-port-about-updated)
  - [Status Updated](#output-port-status-updated)
  - [Settings Changed](#output-port-settings-changed)
  - [Team Member Added / Removed / Updated](#output-port-team-member-added--removed--updated)
- [Technical Asset Events](#technical-asset-events)
  - [Created](#technical-asset-created)
  - [Status Updated](#technical-asset-status-updated)
  - [Updated](#technical-asset-updated)
  - [Deleted](#technical-asset-deleted)
  - [Linked to Output Port](#technical-asset-linked-to-output-port)
  - [Unlinked from Output Port](#technical-asset-unlinked-from-output-port)
- [Information Requirements Summary](#information-requirements-summary)

---

## Platform Setup

### Infrastructure Model

- **Buckets**: Each domain has one S3 bucket. Naming by convention from the domain slug, e.g. `{domain-slug}`.
- **IAM roles**: Each data product has one AWS IAM role named `dpp-{namespace}`. Namespace is the stable, immutable identifier for a data product.
- **S3 prefix**: Each data product's primary home is `s3://{domain-bucket}/{namespace}/`.
- **Technical assets**: Each S3 location (subfolder or existing external location) is registered as a technical asset in the Portal.

### Naming Convention

> **Do not encode the domain name in the IAM role name.** If a data product moves between domains, role names would need to change. IAM role renames require destroying and recreating the role and re-issuing every trust policy for every team member. Use only the namespace — it never changes. We already deliberately add complexity by giving every domain their own bucket.

### Data Product Settings

| Setting | Effect |
|---|---|
| `read-only-role` | Creates a second IAM role `dpp-{namespace}-ro` with read-only access to all of the data product's technical assets |
| `scheduled` | Grants the data product's main IAM role permission to interact with the MWAA instance (e.g. `airflow:CreateCliToken`) |

### Team Roles and Integration Access

Both `owner` and `developer` roles have integration access — users in either role can assume the data product's AWS IAM role.

### Technical Asset Types

| Mapping | Initial Status | Description |
|---|---|---|
| `default` | ACTIVE | The provisioner creates a new subfolder under the domain bucket. Available immediately. |
| `custom` | PENDING | The user registers an existing S3 location. Starts PENDING; must be explicitly activated before it can be linked to output ports or grant any access. |

### Technical Asset Link Approval

A technical asset can be linked to an output port. Linking takes effect immediately — there is no separate approval step for the TA↔OP relationship. The TA's own PENDING / ACTIVE / ARCHIVED status still controls whether it can be linked at all (only ACTIVE TAs can be linked).

---

## Data Product Events

### Data Product Created

The provisioner needs the data product's namespace, domain, type, and the list of initial team members (with their roles).

1. Resolve the domain bucket name from the domain (by convention: `{domain-slug}`).
2. Create the IAM role `dpp-{namespace}`:
   - Trust policy: include all initial team members as principals immediately. Creation always includes at least one owner; do not wait for `team_member_added` events to populate the trust policy.
   - Permission policy: read/write access to `s3://{domain-bucket}/{namespace}/*`.
   - If the data product type confers additional permissions (e.g. cross-account access for a shared type), apply them now.
3. Create the S3 prefix by uploading a placeholder or relying on the first write.
4. Call the Portal API to register the subfolder as a `default` technical asset on this data product. This triggers a `technical_asset.created` event. That handler should be idempotent and see we already have access.
5. Update the data product status from `Draft` to `Ready`.

> **Note**: The data product type may influence the base permissions attached to the IAM role. The exact mapping is platform-specific and should be documented per type. Tags and status could similarly influence permissions, but their semantics are not yet defined.

---

### Data Product Updated

The provisioner needs the data product's namespace, the old and new domain, the new type, and the list of current technical assets (with their S3 configuration).

Only type and domain changes have infrastructure impact.

**Type changed:**

1. Update the IAM role `dpp-{namespace}` to reflect the permission set associated with the new type.

**Domain changed:**

This is the most disruptive change. Proceed carefully:

1. Identify the new domain bucket from the new domain name.
2. Call the Portal API to create a new `default` technical asset pointing to `s3://{new-domain-bucket}/{namespace}/`. Wait for the `technical_asset.created` event to confirm the new prefix is provisioned and the IAM role has access.
3. Copy all data from `s3://{old-domain-bucket}/{namespace}/` to `s3://{new-domain-bucket}/{namespace}/`.
4. For each output port that had the old technical asset linked:
   a. Link the new technical asset to that output port.
   b. For each data product with an approved input port on that output port, grant read access to the new S3 location on their IAM role.
5. Remove read/write access to the old S3 prefix from `dpp-{namespace}`.
6. For each consumer data product identified in step 4b, revoke their access to the old S3 location.
7. Mark the old technical asset as archived via the Portal API.

> **Warning**: This sequence involves multiple Portal API calls that each trigger further events. Design all handlers to be idempotent. Consider how to deal with concurrent updates to the same underlying objects.

**Status changed / Tag changed:**

Infrastructure impact is currently unknown. The provisioner should log these events. Future platform requirements may attach meaning to them (e.g. tags controlling cross-account access, deprecated status suspending the IAM role).

---

### Data Product Deleted

> **Important**: Deletion cascades in the database. Technical assets, output ports, and input port links are all deleted in the same transaction without emitting individual events for each. The provisioner must handle all teardown in this single event.

The provisioner needs the data product's namespace, its settings, the full S3 configuration of each technical asset, and — critically — for each technical asset, the list of consumer data products that had approved read access via any output port exposing that asset. This consumer list is gone from the database by the time the event fires, so it must be available at event dispatch time.

1. For each technical asset in the payload:
   a. Revoke read access to this TA's S3 location from the IAM role of every consumer data product that had approved access.
   b. If `read-only-role` is enabled on any of those consumers, also revoke from `dpp-{consumer-namespace}-ro`.
2. If the `read-only-role` setting was enabled on this data product: delete `dpp-{namespace}-ro`.
3. Delete the IAM role `dpp-{namespace}`.
4. Archive or delete S3 objects under `s3://{domain-bucket}/{namespace}/`.

> **Recovery note**: Restoring a deleted data product requires both data (S3 object) recovery and metadata (dpp database) recovery.

---

### Data Product About Updated

No provisioner action required.

> **Note**: The `about` field holds free-text context about the data product. One use: an AI agent per data product that uses this field as its system prompt. If such an agent is running, this event is the trigger to refresh its instructions.

---

### Data Product Status Updated

No action currently defined.

> **Note**: Possible future interpretation: a `Deprecated` or `Decommissioned` lifecycle status could disable the IAM role or prevent new input port requests. Revisit when lifecycle status semantics are formalised.

---

### Data Product Settings Changed

The provisioner needs to know which setting changed, the data product's namespace, and the full list of its technical assets (to set up the read-only role's permissions) and approved input port links (to grant the read-only role access to consumed data as well). Since the data product still exists at this point, a round-trip to fetch this is acceptable — but knowing at minimum which setting changed and the namespace is required before any round-trip.

**`read-only-role` enabled:**

1. Create IAM role `dpp-{namespace}-ro`.
2. Grant read-only access to all S3 locations of the data product's own technical assets (`s3:GetObject`, `s3:ListBucket` on each `s3://{bucket}/{prefix}/*`).
3. Grant read-only access to all S3 locations of every approved input port (i.e. all TAs the data product already has approved access to via its input ports).
4. Apply the same trust policy as the main role so all current team members can also assume the read-only role.

**`read-only-role` disabled:**

1. Delete `dpp-{namespace}-ro`.

**`scheduled` enabled:**

1. Update `dpp-{namespace}` to allow interaction with the MWAA instance (e.g. attach a policy granting `airflow:CreateCliToken` scoped to the instance ARN, or allow the role to assume the MWAA execution role).

**`scheduled` disabled:**

1. Remove the MWAA-related permissions from `dpp-{namespace}`.

---

### Team Member Added

Both `owner` and `developer` have integration access. The provisioner needs the data product's namespace, the user's email (to resolve their AWS principal), and their role.

1. Resolve the user's AWS principal (IAM user ARN or SSO identity) from their email.
2. Add the principal to the trust policy of `dpp-{namespace}`.
3. If `read-only-role` is enabled: also add the principal to the trust policy of `dpp-{namespace}-ro`.

---

### Team Member Removed

The provisioner needs the data product's namespace, the user's email, and their role.

1. Resolve the user's AWS principal from their email.
2. Remove the principal from the trust policy of `dpp-{namespace}`.
3. If `read-only-role` is enabled: also remove the principal from the trust policy of `dpp-{namespace}-ro`.

---

### Team Member Updated (role changed)

Since both `owner` and `developer` have integration access, a role change does not require any change to the IAM trust policy. No action required.

> **Note**: If future roles are introduced without integration access, the provisioner would need the user's email, and their new role. They can then read the roles of the data product to decided whether to add or remove the principal from the trust policy. 
The old role is not needed since the provisioner can just check all roles

---

### Input Port Requested

Event fires when a data product requests access to an output port. For **unrestricted** output ports the link is automatically approved at request time. For **restricted** output ports the link starts as PENDING — no action until `output_port.link_approved` fires.

The provisioner needs the requesting data product's namespace and settings, the link status at the time of the event (APPROVED or PENDING), and the S3 configuration of the technical assets behind the output port. Without knowing the link status the provisioner cannot distinguish the unrestricted (act immediately) from the restricted (wait for approval) case.

If link status is **APPROVED**:

1. For each technical asset linked to the output port, grant read access (`s3:GetObject`, `s3:ListBucket`) on `dpp-{requesting-namespace}`.
2. If `read-only-role` is enabled on the requesting data product: apply the same grants to `dpp-{requesting-namespace}-ro`.

If link status is **PENDING**: no action. Wait for `output_port.link_approved`.

---

### Input Port Request Approved

Fires when the output port owner approves a pending access request.

The provisioner needs the requesting data product's namespace and settings, and the S3 configuration of the technical assets behind the output port.

1. For each technical asset linked to the output port, grant read access on `dpp-{requesting-namespace}`.
2. If `read-only-role` is enabled on the requesting data product: apply the same grants to `dpp-{requesting-namespace}-ro`.

---

### Input Port Request Denied

No action required. The link was PENDING; no access was ever granted.

---

### Input Port Removed

Fires when a data product's access to an output port is removed. This can happen to both approved and pending links.

The provisioner needs the requesting data product's namespace and settings, the link status at the time of removal (APPROVED or PENDING), and the S3 configuration of the technical assets behind the output port. Without the status the provisioner would need to check the AWS to tell whether access was ever granted and therefore whether there is anything to revoke.

If the link was **APPROVED**:

1. For each technical asset that was linked to the output port, check whether the requesting data product still has access to the same TA via another approved input port.
2. For any TA no longer accessible via another path: revoke read access from `dpp-{requesting-namespace}`.
3. If `read-only-role` is enabled: also revoke from `dpp-{requesting-namespace}-ro`.

If the link was **PENDING**: no action. No access was ever granted.

---

## Exploration Events

Explorations are lightweight workspaces owned by a single user. Unlike data products they have no output ports, no technical assets, and no settings. Their sole purpose is to consume data from approved input ports.

The provisioner creates an IAM role for the exploration so the owner can assume it to access S3 locations they have been granted read access to via input ports. No S3 prefix is created — explorations do not produce or store data.

### Exploration Created

The provisioner needs the exploration's namespace and the owner's identity.

1. Create IAM role `dpp-{namespace}` with the owner as the sole principal in the trust policy.
2. Update the exploration status from `Draft` to `Ready`.

> Explorations do not own storage — no S3 prefix or technical asset is created.

---

### Exploration Deleted

The provisioner needs the exploration's namespace.

1. Delete the IAM role `dpp-{namespace}`.

No S3 cleanup is needed since explorations own no storage.

---

### Exploration Input Port Requested

Same logic as [Input Port Requested](#input-port-requested) for data products.

The provisioner needs the exploration's namespace, the link status (APPROVED or PENDING), and the S3 configuration of the technical assets behind the output port.

If link status is **APPROVED**:

1. For each technical asset linked to the output port, grant read access (`s3:GetObject`, `s3:ListBucket`) on `dpp-{exploration-namespace}`.

If link status is **PENDING**: no action. Wait for `output_port.link_approved`.

---

### Exploration Input Port Request Approved

Same logic as [Input Port Request Approved](#input-port-request-approved) for data products.

The provisioner needs the exploration's namespace and the S3 configuration of the technical assets behind the output port.

1. For each technical asset linked to the output port, grant read access on `dpp-{exploration-namespace}`.

---

### Exploration Input Port Request Denied

No action required.

---

### Exploration Input Port Removed

Same logic as [Input Port Removed](#input-port-removed) for data products.

The provisioner needs the exploration's namespace, the link status at removal time, and the S3 configuration of the technical assets behind the output port.

If the link was **APPROVED**:

1. For each technical asset that was linked to the output port, check whether the exploration still has access via another approved input port.
2. For any TA no longer accessible via another path: revoke read access from `dpp-{exploration-namespace}`.

If the link was **PENDING**: no action.

---

## Output Port Events

### Output Port Created

No action required.

---

### Output Port Updated

No action required.

---

### Output Port Deleted

> **Important**: Technical assets are owned by the data product, not by the output port. Deleting an output port does **not** delete the technical assets. It removes the links between the output port and its TAs. The data product retains all its technical assets.

The provisioner needs the S3 configuration of the technical assets that were linked to this output port, and the list of consumer data products (with their namespace and settings) that had approved input port access. Both are gone from the database after deletion, so they must be available at event dispatch time.

1. For each consumer data product with an approved input port on this output port:
   a. For each TA that was linked to this output port, check whether the consumer still has access to the same TA via another approved input port.
   b. For any TA no longer accessible via another path: revoke read access from `dpp-{consumer-namespace}`.
   c. If `read-only-role` is enabled on the consumer: also revoke from `dpp-{consumer-namespace}-ro`.

---

### Output Port About Updated

No action required.

---

### Output Port Status Updated

No action currently defined. Future interpretation: a deprecated output port status could prevent new input port requests or trigger access revocation.

---

### Output Port Settings Changed

Depends on the setting. Output port settings are not yet fully defined for this platform.

> **TODO**: Clarify what settings live under output ports. A possible future example: an encryption requirement setting could enforce an SSE-KMS condition on all S3 read operations for this output port's technical assets.

---

### Output Port Team Member Added / Removed / Updated

Output ports have their own role assignments — users can be granted roles such as approver (the ability to approve or deny access requests to the output port). These are Portal-level roles with no AWS infrastructure equivalent.

No infrastructure action required.

> **Note**: Future platform requirements could introduce output-port-level IAM grants — for example, granting a specific user direct S3 read access to the output port's technical assets without going through a data product input port. If that is introduced, these events would be the trigger. For now they are informational only.

---

## Technical Asset Events

### Technical Asset Created

The provisioner needs the owning data product's namespace, settings, the technical mapping (default or custom), and the S3 configuration (bucket, prefix or location).

**Default (portal-managed subfolder):**

1. Create the S3 prefix (upload a placeholder object if needed) to s3://{domain}/{namespace}/{path}.

> **Note**: The IAM Roles already have already have `s3://{domain}/{namespace}/*` access so no need to update.

**Custom (user-registered existing location):**

The technical asset starts as PENDING. No IAM changes until it is activated. See `technical_asset.status_updated`.

---

### Technical Asset Status Updated

Applies primarily to `custom` technical assets transitioning from PENDING to ACTIVE, and to any asset being archived.

The provisioner needs the owning data product's namespace and settings, the S3 configuration of the asset, and both the old and new status. Without the old status the provisioner cannot determine whether this is an activation (PENDING → ACTIVE) or an archival.

**PENDING → ACTIVE:**

1. Grant read/write access to the registered S3 location on `dpp-{namespace}`.
2. If `read-only-role` is enabled: also grant read-only access on `dpp-{namespace}-ro`.

**ACTIVE → ARCHIVED:**

1. Revoke the owning data product's access to this S3 location from `dpp-{namespace}` and `dpp-{namespace}-ro`.
2. For each output port that had this TA linked, and for each consumer data product with an approved input port on that output port: revoke their read access (same logic as `technical_asset.deleted` below).

---

### Technical Asset Updated

S3 locations cannot be moved or renamed after creation. No action required.

---

### Technical Asset Deleted

The provisioner needs the owning data product's namespace and settings, the S3 configuration of the asset, and — for each output port this TA was linked to — the list of consumer data products with approved access. The latter is gone from the database after deletion and must be available at event dispatch time.

1. Revoke the owning data product's own access to this S3 location from `dpp-{namespace}`.
2. If `read-only-role` is enabled on the owning data product: revoke from `dpp-{namespace}-ro`.
3. For each output port this TA was linked to:
   a. For each consumer data product with an approved input port on that output port:
      - Check whether the consumer still has access to this S3 location via another TA on another output port.
      - If not: revoke read access from `dpp-{consumer-namespace}`.
      - If `read-only-role` is enabled on the consumer: also revoke from `dpp-{consumer-namespace}-ro`.
4. Delete S3 objects at this location (or archive, per retention policy).

---

### Technical Asset Linked to Output Port

Fires when a data product owner links a technical asset to an output port.

> **Note**: The separate approve/deny flow for TA↔OP links is being removed. This event is the effective trigger for granting consumer access.

The provisioner needs the S3 configuration of the technical asset and the list of consumer data products (with their namespace and settings) that have approved input port access to this output port.

1. For each consumer data product with an approved input port on this output port:
   a. Grant read access to this TA's S3 location on `dpp-{consumer-namespace}`.
   b. If `read-only-role` is enabled on the consumer: also grant on `dpp-{consumer-namespace}-ro`.

---

### Technical Asset Unlinked from Output Port

Fires when a technical asset is removed from an output port.

The provisioner needs the S3 configuration of the technical asset and the list of consumer data products (with their namespace and settings) that had approved input port access to this output port at the time of removal.

1. For each consumer data product that had approved input port access to this output port:
   a. Check whether the consumer still has access to this TA via another output port.
   b. If not: revoke read access from `dpp-{consumer-namespace}`.
   c. If `read-only-role` is enabled on the consumer: also revoke from `dpp-{consumer-namespace}-ro`.

---

## Information Requirements Summary

This table captures information the provisioner needs that is not trivially available at event dispatch time. It is intended as input for event design.

| Event | Information needed | Why |
|---|---|---|
| `data_product.created` | Initial team members with their roles | Trust policy must be populated at creation, not via subsequent events |
| `data_product.deleted` | Per-TA: list of consumers with approved access | Object is already gone; provisioner must revoke consumer access |
| `data_product.input_port_linked` | Link status (APPROVED / PENDING) | Provisioner must distinguish unrestricted (act now) from restricted (wait) |
| `data_product.input_port_unlinked` | Link status at removal time | Provisioner must know whether access was ever granted |
| `output_port.deleted` | Linked TAs + approved consumers per TA | Objects are gone; provisioner must revoke consumer access |
| `technical_asset.deleted` | Per-linked-OP: list of consumers with approved access | Object is gone; provisioner must revoke consumer access |
| `technical_asset.status_updated` | Old status | Provisioner must know whether this is an activation or an archival |
| `technical_asset.linked` | List of consumers with approved input port access to the output port | Provisioner must grant access to all existing consumers |
| `technical_asset.unlinked` | List of consumers with approved input port access to the output port | Provisioner must revoke access from all current consumers |
| `exploration.created` | Owner identity | IAM role trust policy must include the owner |
| `exploration.input_port_linked` | Link status (APPROVED / PENDING) | Same as data product: must distinguish unrestricted from restricted |
| `exploration.input_port_unlinked` | Link status at removal time | Must know whether access was ever granted |
