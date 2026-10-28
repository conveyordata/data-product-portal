# Data product visibility

## Context and Problem Statement

We will add a `visibility` field to data products with two states: `discoverable` and `hidden`. Hidden data products should
only be visible to users with an approved role on the product, while discoverable data products should be visible to any
authenticated user.

Currently there is already such an implementation for Output Ports, however there are some holes in the implementation.
For example sub routers of output port like: contract, data quality etc do not check for visibility and thus can leak information on hidden output ports.

We do not want to repeat these mistakes.

We currently already use Casbin for authorization and resource-scoped role assignments. There is an opportunity to keep visibility
decisions in the same system instead of adding a separate application-side check that can drift from the RBAC model or be missed on nested routes.

This requirement applies not just to the data product detail route, but also to child resources under a product,
such as technical assets and services. We need the visibility decision to be centralized, auditable, and consistent across all product-scoped routes.

We also want to reuse this mechanism for Input Ports, and the list of consumers for Output Ports. Hidden Data Products to
which you do not have access should be redacted from the list. Only public information should be visible: ID, requester (so you know whom to talk to when reviewing), business reason etc.
Not the name of the Data Product, description ...
So we should be able to reuse the same mechanism, for these list calls. This will not be possible through endpoint
dependency checks, the service itself will have to do filtering and redaction based on the visibility of the product.


## Decision Drivers

* Align visibility enforcement with the existing Casbin authorization model
* Reuse the current data-product assignment flow instead of introducing a second access mechanism
* Keep discoverable products available to any authenticated user without per-user allowlisting
* Avoid route-by-route checks that are easy to miss on nested or derived routes
* Preserve the existing assignment approval and revocation flow for hidden products
* Keep the implementation predictable as product visibility changes over time
* The visibility enforcement should also be usable in certain list calls where we need to redact information, such as Input Ports list, or consumers of Output Ports

## Considered Options

* **Option 1: Application-layer visibility dependency** Application-side dependency on product routes that checks `visibility` and approved assignments directly
* **Option 2: Casbin resource-role visibility** Reuse approved data-product assignments for hidden products and add a wildcard public role for discoverable products
* **Option 3: ORM based visibility** Via the ORM we can ensure that only visibilit data products are returned in calls

## Decision Outcome

**Chosen option:** *Option 2: Casbin resource-role visibility* and **Option 3: ORM based visibility**. We will keep visibility
enforcement inside Casbin and reuse the existing data-product assignment flow for the restricted-user path.

The model is:

* Hidden products are authorized through the existing approved role-assignment path.
* Discoverable products are granted a `public_reader` resource role through a wildcard group entry for the product.
* The Casbin matcher is extended to allow public resource-role groupings such as `g("*", role, product_id)`.

The data product `visibility` field remains the source of truth, while Casbin remains the enforcement engine.
The application keeps Casbin and the database in sync when a product is created, when visibility changes, and when assignments are approved, denied, or revoked.

The reason for adding ORM based visibility is to reduce the change of mistakes.

### Confirmation

This will be reflected in the application as follows:

* Add a data-product read action to the authorization enum.
* Keep the current approved data-product assignment flow as the mechanism for hidden-product access.
* Create a `public_reader` role and attach it to a product when `visibility == discoverable`.
* Use the existing resource-role model with a wildcard subject such as `g("*", public_reader_role_id, product_id)`.
* Update the Casbin matcher to allow wildcard public resource-role groupings during enforcement.
* When product visibility changes, update Casbin groupings to match the product row state.
* When assignments are approved or revoked, continue through the existing assignment sync logic for the assigned-user case.
* Enforce access at the route layer through the standard authorization flow without app-side visibility checks on each endpoint.

## Pros and Cons of the Options

### Option 1: Application-layer visibility dependency

* **Good, because** it is straightforward to implement and easy to reason about in code.
* **Good, because** can be easily reused to redact information in list calls, such as Input Ports list or Output Port consumers.
* **Neutral, because** it matches the product business rules directly and does not require Casbin synchronization.
* **Bad, because** it creates a second authorization mechanism that can drift from Casbin and is easy to omit on nested routes.
* **Bad, because** the rule becomes spread across route dependencies and service methods, which makes maintenance harder.
* **Bad, because** same risk as output port visibility, where some routes check for visibility and some don't, leading to potential information leaks.

### Option 2: Casbin resource-role visibility

* **Good, because** it keeps visibility decisions in the same authorization system as all other data-product access.
* **Good, because** it reuses the existing approved assignment flow for hidden products and avoids a second permission model.
* **Good, because** discoverable products are represented as a public resource role, which fits the existing Casbin grouping model.
* **Good, because** we can easily check if all routes have casbin enforcement through a test, instead of now where some routes have casbin enforcement and some don't.
* **Good, because** doesn't repeat the same security loopholes that where present in Output Port visibility.
* **Good, because** can be reused to redact information in list calls, such as Input Ports list or Output Port consumers.
* **Bad, because** the application must keep Casbin state synchronized with product visibility and assignment changes. If someone changes the DB directly, we will run into issues. But this is never recommended anyway, so this is not a big issue.
* **Bad, because** it introduces policy synchronization and thus requires careful handling when a product changes from hidden to discoverable or vice versa.
* **Bad, because** the matcher must support wildcard public groupings without breaking the existing RBAC semantics.

### Option 3: ORM based visibility

* **Good, because** you make it hard to abuse
* **Neutral, because** raw queries skip it, but we can reduce raw queries
* **Bad, because** it is hidden

## Implementation Notes

The implementation will use the existing data-product role assignment flow as the restricted-user path and add one public product role for discoverable products.

The notable changes are:

* Add `DATA_PRODUCT__READ` to the action enum.
* Add `public_reader` as a resource role with `DATA_PRODUCT__READ` permission.
* Update the Casbin matcher to allow `g("*", role, product_id)` for public reads.
* When a product becomes discoverable, create the wildcard public grouping.
* When a product becomes hidden, revoke the wildcard public grouping.
* When a user is approved for a hidden product, the existing assignment flow already creates the user-specific group.
* When approved assignments are revoked or denied, the existing revoke logic removes the user-specific group.

This keeps authorization centralized and avoids a second visibility enforcement layer.
