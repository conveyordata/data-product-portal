---
sidebar_position: 200
---

# Release Notes

## Unreleased

## 0.5.0

This migration can take some time, depending on the amount of output ports present, as embeddings are calculated for every output port.

### features

- **[API Migration]**: Added the [API v2 migration](./technical-reference/api-v2.md) to the docs.
- **[Data quality]**: Support ingesting data quality summary data and showing the overall status on output ports.
  For more details look at the [data quality documentation](./developer-guide/data-quality-information.md)
- **[Technical Mapping]**: Reworked source aligned concepts to [technical mapping ](./concepts/technical-assets.md#%EF%B8%8F-technical-mapping)
- **[Search]**: Improved search functionality in the marketplace, the search now understands the context of the search term.
- **[Product Studio]**: The product studio is the new location to manage your data products and output ports. You can view and edit all your data assets in one convenient location.
- **[Technical Asset Configuration]**: We have migrated away from a single table for configurations. Each plugin type now has it's own table. Make sure to write a migration script for your own technologies as well.
- **[Technical Integration Plugins]**: Technical integrations are now provided from the backend, including the behavior of the access tiles and form generation. They can be enabled or disabled via environment variables.
- **[Pending Requests]**: Pending requests are now visible inside the product studio as well and will be migrated away from the homepage in future versions.
- **[Docs]**: Added a FAQ section to the docs about Data Product thinking.

### bugfixes

- **[Marketplace]**: Fixed an issue where long domains could result in inconsistent sizing of the cards
- **[Team]**: Fixed an issue where added members did not get the correct rights assigned.

### deprecations

- **[API]**: Full v1 version of the API is deprecated and will be removed in 0.6.0

## 0.4.2

### features
- **[Usage]**: Added usage tabs with curated queries and query statistics on data products. This feature is still in Beta.

- **[Explorer]**: Removed technical assets from full explorer view for clarity. Improved performance of graph fetching.

- **[Admin rights]**: It is no longer allowed to have permanent admin rights. Users who were admins before will now get the option to temporarily elevate themselves to super user rights.
This avoids the pitfall where you permanently are allowed to do everything and no longer have a view on how the normal user flow looks.

- **[API]**: We are working on a v2 version of the API, we have already migrated the endpoints:
  - `/api/data_product_lifecycles` -> `/api/v2/configuration/data_product_lifecycles`
  - `/api/data_product_settings` -> `/api/v2/configuration/data_product_settings`
  - `/api/data_product_types` -> `/api/v2/configuration/data_product_types`
  - `/api/domains` -> `/api/v2/configuration/domains`
  - `/api/environments` -> `/api/v2/configuration/environments`
  - `/api/platforms` -> `/api/v2/configuration/platforms`
  - `/api/tags` -> `/api/v2/configuration/tags`
  - `/api/theme_settings` -> `/api/v2/configuration/theme_settings`
  - `/api/authz` -> `/api/v2/authz`
  - `/api/role_assignments/dataset` -> `/api/v2/authz/role_assignments/output_port`
  - `/api/role_assignments/data_product` -> `/api/v2/authz/role_assignments/data_product`
  - `/api/role_assignments/global` -> `/api/v2/authz/role_assignments/global`
  - `/api/roles` -> `/api/v2/authz/roles`

### bugfixes
- **[Explorer]**: Removed dangling pointers when disabling certain types. Show datasets in view if they don't have technical assets added yet.

## 0.4.1

### features
- **[Shopping experience]**: We have added a new shopping experience, which allows you to add output ports to your cart,
  and request access to multiple output ports at once. We also added the required field, business justification to the
  access requests. This will help the reviewer of your access request understand why access is needed.
- **[Product Tour]**: Shows a small tutorial upon creation of your first data product.
- **[Marketplace search]**: Support searching for data outputs using name and description as well as its technical assets.

### bugfixes
- **[MCP]**: Fixed OAuth issues with MCP server.

### deprecations
- **[API]**: Deprecated `/api/data_products/{id}/dataset/{dataset_id}` POST endpoint, use `/api/data_products/{id}/link_datasets` instead.

## 0.4.0

- Rename data outputs to technical assets
- Rename datasets to output ports

### features

- **[Output Ports]**: Breaking change: Output ports are now tightly coupled to exactly one Data Product.
- **[Technical Assets]**: Added drag and drop flow.
- **[Marketplace]**: Reworked marketplace UX.

### bugfixes

- **[UX]**: Various UX bugs, pagination, ...

## 0.3.7

### features

- **[Products]**: Added filtering on roles.
- **[Docs]**: Proper URL.

### bugfixes

- **[History]**: Deletes caused not found errors in frontend.
- **[Backend]**: Fix detached instance errors, also fixes mails.

## 0.3.6

### features

- **[Explorer]**: Introduce domain nodes and new layout algorithm
- **[Backend]**: Performance optimization for queries.
- **[Helm]**: Add default MCP paths to ingress default values
- **[MCP]**: Extend tools with roles functionality, more visibility for experiment, rollback OAuth lib update

### bugfixes

- **[Posthog]**: Correct disabling of analytics
