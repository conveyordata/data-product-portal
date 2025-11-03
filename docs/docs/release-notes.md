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

## 0.3.6

### features

- **[Explorer]**: Introduce domain nodes and new layout algorithm
- **[Backend]**: Performance optimization for queries.
- **[Helm]**: Add default MCP paths to ingress default values
- **[MCP]**: Extend tools with roles functionality, more visibility for experiment, rollback OAuth lib update

### bugfixes

- **[Posthog]**: Correct disabling of analytics
