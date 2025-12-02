# ADR Title

## Context and Problem Statement

The current API's don't match the naming of output ports and technical assets.
Also because of [ADR 0001 - Datasets Belong to a Single Data Product](0001-datasets-single-parent.md) output ports
are always part of a single data product.
The API's are currently also split up quite a lot so there are opportunities to fix this


## Decision Drivers

* Outport, and technical asset rename
* [ADR 0001 - Datasets Belong to a Single Data Product](0001-datasets-single-parent.md)
* Api's very granular

## Considered Options

* **Option 1: Rename the current API's** Only rename output ports and technical assets.
* **Option 2: Migrate to a v2 API** This option renames and aggregates the API's to make them more coherent.

## Decision Outcome

**Chosen option:** *Option 2: Migrate to a v2 API*. Since we have to deprecate a lot of API endpoints anyway, we can take the opportunity to do this.

### Confirmation

There will be a new v2 api version, and the old API's will be deprecated.

## Pros and Cons of the Options

### Option 1: Title Option 1

* **Good, because**
  * Simple to execute
  * Less deprecation
* **Neutral, because**
  * We want to start generating the Front end API from the OpenAPI spec later anyway, so we need to rewrite the front end
* **Bad, because**
  * Missed opportunity to clean up the API's, and make them more coherent

### Option 2: Title Option 2

* **Good, because**
  * Opportunity to make the API's more coherent
  * We need to rewrite the front end anyway because we want to generate it from the OpenAPI spec, so this is a good time to do it
* **Bad, because**
  * Longer migration


## Appendix

### V2 api design

This document lists the current services, and their root URL path, and how we want to change them for a v2 design.


#### datasets: /api/datasets

Propose to move under data products: /api/v2/data_product/{id}/output_port

However search/list for datasets must be a different thing, since it lists/searches across data products.

Remove namespace methods, and [migrate them](#namespace-methods)
namespace suggestion
validate namespace
namespace lenght limits

#### Data products: /api/data_products

Just make this v2.

Remove namespace methods, and [migrate them](#namespace-methods)
namespace suggestion
validate namespace
namespace lenght limits

URL links => Rename to /api/v2/data_product/{id}/url where you pass a type as parameter

#### Data product types: /api/data_product_types

Propose to move to /api/v2/configuration/data_product_types

Everything will be under the configuration service.

Similar for:
data_product_lifecycles
data_product_settings
domains
environments
platforms
tags
theme_settings

#### Namespace methods

The namespace methods currently help to check if a namespace is valid for a cloud.

I would suggest to rename this to either:
- resource_names, with the methods
  - /resource_names/sanitize
  - /resource_names/validate
  - /resource_names/contraints (max length and maybe other constraints)
- slug (in web development a slug is a url friendly version of a string, in our case it's a cloud friendly version)
  - /slugs/sanitize
  - /slugs/validate
  - /slugs/contraints (max length and maybe other constraints)

Preferred option is: resource_names

Namespace endpoints can be removed from output ports, data products etc and move here


#### data_product_dataset_links: /api/data_product_dataset_links

Move to /api/v2/data_product/{id}/input_ports, the link methodes are also here.

We do need a method to get all pending users actions however. However the current method is unused, and the method already exists


#### data_output_dataset_links: /api/data_output_dataset_links

Move to /api/v2/data_product/{id}/technical_assets

They always belong to data products.
We do need a method to get all pending users actions however. However the current method is unused, and the method already exists

#### data_outputs: /api/data_outputs

Move to /api/v2/data_product/{id}/technical_assets

#### users: /api/users

Move to /api/v2/users

We could add pending actions here:
/api/v2/users/current/pending_actions this could support all pending actions, with a filter if needed. This method already exists

Rename tour endpoint:
/api/v2/user/current/seen_tour

#### authz: /api/authz
#### roles: /api/roles
#### role_assignments: /api/role_assignments

I would migrate this into one authz endpoint:
/api/v2/authz

Current dataset roles need to be revised, but for now we just rename them. Fixing this is put on our roadmap.

There are currently also patch calls here, but this is very inconsistent with the rest of the API. So the proposal is to
make them PUT calls, when they are idempotent, POST calls otherwise.

#### Graph: /api/graph

Current very technical method naming, this is OK. Only used in explorer, similar to search.

#### Notifications: /api/notifications

Move to /api/v2/users/current

#### pending_actions: /api/pending_actions

move to users current user

#### events: /api/events/latest

Unused. Idea was to have a lambda call this to see if events have happened to update the infra.
We can currently remove it

#### auth: /api/auth

Renamed to /api/v2/authn

Has duplicated method with device flow, so the device flow service for now

#### mcp:

Currently leave it like this, look into migrating /api/v2/register

#### default

Remove / endpoint, or is this a health check. If it's a used health check move to private API that is not exposed, and make it /api/v2/health.

Move version to info tag, and /api/v2/version
