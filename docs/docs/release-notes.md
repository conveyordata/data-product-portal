---
sidebar_position: 200
---

# Release Notes

## Unreleased

### features
- **[Shopping experience]**: We have added a new shopping experience, which allows you to add output ports to your cart,
  and request access to multiple output ports at once.

### deprecations:
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
