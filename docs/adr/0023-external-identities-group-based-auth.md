# Support Groups and Machine Users as Assignable Identities

## Context and Problem Statement

Portal currently represents users as the only type of identity. Global and Data Product role assignments reference `users.id`, meaning groups and machine users
cannot receive these roles.

Portal wants to extend its authorization model so a Global or Data Product role can be assigned to a user, group or machine user. If a group receives a role,
every user belonging to that group must inherit the related permissions and visibility as if the assignment had been made directly to the user.

Only users can authenticate and operate Portal. Groups and machine users are non-interactive identities that can receive role assignments, while users and
machine users can be members of groups.

Explorations currently use a user-specific ownership model and can therefore only be owned and operated by users. Extending Explorations to support the common
Identity model requires a separate refactoring and is outside the scope of this decision.

Portal needs also a way to introduce these identities from an external identity provider and a way to expose them through the API.

## Decision Drivers

* Allow users, groups and machine users to receive Global and Data Product roles through the same assignment model.
* Keep users as the only identity type that can authenticate and operate Portal.
* Grant users permissions and Data Product visibility inherited from their groups.
* Use a standard protocol for synchronizing users, groups and memberships.
* Support machine users even when they are not available through SCIM.
* Provide provider-agnostic APIs for identities, memberships and Data Product role assignments.
* Preserve existing user-linked workflow and audit relationships.
* Avoid nested-group resolution, as the supported identity provider supplies flat memberships.
* Keep the current user-specific Exploration model unchanged.

## Considered Options

* **Option 1: Common Identity with separate subtype tables** — add an `identities` table referenced by `users`, `groups` and `machine_users`, with each subtype
  using the Identity ID as its primary and foreign key.
* **Option 2: Single Identities table** — store users, groups and machine users in one table, using a type discriminator and nullable type-specific columns.

For synchronization:

* **Option A: Extend Portal API** — receive every identity type and membership through Portal-specific API operations.
* **Option B: Extend Portal API + SCIM interface** — receive users, groups and memberships through SCIM and receive machine users through a Portal-specific
  API.

## Decision Outcome

**Chosen options:** *Option 1: Common Identity with separate subtype tables* and *Option B: Extend Portal API + SCIM interface*.

A common Identity provides one target for Global and Data Product role assignments while keeping the attributes and behaviour of users, groups and machine users
separated. Only users can authenticate, request or approve changes and act inside Portal, while every identity type can receive roles and both users and machine
users can belong to groups.

Portal will implement a SCIM interface for users, groups and group memberships. Machine users and their memberships will be created and updated through Portal 
API operations until they can be synchronized through SCIM. Both entry points will use the same internal identity services and persistence model.

### Confirmation

* The database contains `identities`, `users`, `groups`, `machine_users` and `group_memberships`.
* Global and Data Product role assignments reference `identities.id`.
* Workflow fields such as `requested_by_id` and `decided_by_id` continue to reference users.
* A user receives access from both direct role assignments and roles assigned to their groups.
* Global authorization and Data Product visibility consider the groups of the authenticated user.
* Explorations continue to use their existing user-specific ownership model.
* SCIM endpoints support the user, group and membership operations required by the identity provider.
* The Portal API supports creating and updating machine users and their group memberships.
* CRUD endpoints expose users, groups, machine users and group memberships.
* Data Product role-assignment responses include the assigned identity and its type.
* The generated SDK includes the new Portal API operations.

## Pros and Cons of the Options

### Option 1: Common Identity with separate subtype tables

* **Good, because** it provides one consistent target for Global and Data Product role assignments.
* **Good, because** type-specific attributes and relationships remain in separate tables.
* **Good, because** users remain separated from identities that cannot authenticate.
* **Good, because** group membership can reference both users and machine users.
* **Good, because** Casbin group inheritance can be used to enforce access control policies.
* **Neutral, because** reading a complete identity requires joining its common and type-specific tables.
* **Bad, because** parent and subtype rows must be managed in the same transaction.
* **Bad, because** Portal must validate that every Identity has exactly one subtype matching its type.

### Option 2: Single Identities table

* **Good, because** it requires fewer tables and joins.
* **Good, because** there is no possibility of a missing subtype row.
* **Neutral, because** application code must use the type discriminator to interpret each identity.
* **Bad, because** type-specific columns remain null for other identity types.
* **Bad, because** user-only relationships and constraints become harder to enforce.
* **Bad, because** existing Portal code assumes a dedicated User model for authentication, notifications and workflows.

### Option A: Extend Portal API

* **Good, because** every identity type follows the same synchronization contract.
* **Good, because** Portal keeps control over validation and database writes.
* **Bad, because** it requires designing and maintaining an external custom synchronization protocol.
* **Bad, because** identity providers require a custom integration instead of using their existing SCIM support.

### Option B: Extend Portal API + SCIM interface

* **Good, because** SCIM provides a standard interface for users, groups and memberships.
* **Good, because** the identity provider pushes changes without Portal scheduling provider queries.
* **Bad, because** two synchronization mechanisms must coexist while machine users are not available through SCIM.

## Design Details

### Identity model

The common table holds the Portal identity and its type. Users, groups and machine users use the Identity ID as their primary key and as a foreign key to
`identities.id`.

```mermaid
erDiagram
    identities {
        string id PK
        string type "USER | GROUP | SP"
    }

    group_membership {
        string group_id PK, FK
        string member_id PK, FK
    }

    users {
        string id PK, FK
        string email
        string external_id
        string first_name
        string second_name
    }

    service_principals {
        string id PK, FK
        string display_name
        string external_id
    }

    groups {
        string id PK, FK
        string display_name
        string external_id
    }

    identities ||--o| users : "1:0..1"
    identities ||--o| service_principals : "1:0..1"
    identities ||--o| groups : "1:0..1"
    identities ||--o{ group_membership : "member_id"
    groups ||--o{ group_membership : "group_id"

```

`group_memberships` uses `(group_id, member_identity_id)` as its composite primary key. Portal accepts users and machine users as members and rejects groups as
members. This matches the flat memberships supplied by the supported identity provider and avoids introducing recursive group resolution.

Global and Data Product role assignments reference the common identity:

```text
Identity → Global role
Identity → Data Product role
```

Fields that represent assignment targets reference identities, while fields that represent Portal actors remain attached to users:

```text
identity_id      → identities.id
requested_by_id  → users.id
decided_by_id    → users.id
```

Existing Global and Data Product role assignments must be migrated by creating an Identity row for every existing user and replacing their assignment `user_id`
references with the corresponding `identity_id`.

Explorations remain associated with users through their existing ownership model. Their relationships are not migrated to `identities.id` by this decision.

### Exploration scope boundary

Explorations remain personal resources owned and operated by authenticated users. The current Exploration model references `users.id`, and its authorization
checks compare the owner with the authenticated user.

Supporting groups or machine users in this relationship would require refactoring Exploration ownership and authorization to use the common Identity model. The
expected roles, sharing behaviour and inherited permissions require a separate decision and are not defined in this ADR.

### SCIM interface

Portal exposes a SCIM v2 interface for users and groups, including the discovery endpoints required by the identity provider:

```text
/scim/v2/Users
/scim/v2/Groups
/scim/v2/ServiceProviderConfig
/scim/v2/ResourceTypes
/scim/v2/Schemas
```

The interface supports the filtering, pagination and PATCH operations required by the supported SCIM integration. Group membership is received through the SCIM
Group resource and stored in `group_memberships`.

Portal uses its own Identity UUID as the SCIM resource `id` and stores the identity-provider identifier separately as `externalId`. SCIM operations use the same
internal identity services as the rest of Portal.

Login-time user creation remains supported. SCIM must reconcile with an existing user when both records represent the same external identity instead of creating
a duplicate.

### Portal API

Portal adds authenticated and idempotent CRUD operations for: 

* Users.
* Groups and their members.
* Machine users.
* Data Product role assignments.

The existing `GET /v2/users` operation will be extended where needed as it is already implemented. New operations for groups, memberships and
machine users follow the same `/v2` API conventions.

Data Product role-assignment responses embed the assigned identity and its type. For example, when Group A is Developer of a Data Product, the response contains
Group A rather than the corresponding Identity A:

```json
{
  "data_product_id": "data-product-id",
  "role": {
    "id": "role-id",
    "name": "developer"
  },
  "identity": {
    "id": "identity-id",
    "type": "group",
    "external_id": "external-group-id",
    "display_name": "Group A"
  },
  "decision": "approved"
}
```

Embedding the identity avoids an additional lookup while preserving the original assignment.

Global role assignments are not added to the external read API because they only affect authorization inside Portal.