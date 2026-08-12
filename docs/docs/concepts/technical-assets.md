---
id: technical-assets
title: Technical Assets
sidebar_position: 3
---

# Technical Assets

**Technical Assets** are the individual data entities that are managed by a Data Product.
They represent the actual, physical data that is owned by a Data Product.

## Examples

- An S3 path (e.g. `s3://sales-data/transactions/2024/`)
- A table in a database (e.g. `analytics.sales_transactions`)
- A Kafka topic (e.g. `sales-events-stream`)
- A REST API (`GET /sales/transactions`)

## Governance

Each Technical Asset is registered, versioned, and described with:
- Access control rules
- Technical schema and metadata
- Ownership information

Consumers cannot access these assets directly.
Instead, Data Products offer Output Ports, which bundle a collection of related assets together to provide managed read access.
Output Ports should follow the advice that data that belongs together should also be shared together.

## Technical Mapping

When creating a Technical Asset, you can choose between two provisioning strategies:

### Default Mapping
This is the **recommended option for most users**. Default mapping uses the platform's standard provisioning conventions,automatically generating technical identifiers (paths, table names, schemas, etc.) based on your Data Product's namespace and configuration.

**Benefits:**
- Follows organizational naming conventions
- Receives **implicit approval** from platform owners
- Faster provisioning without manual review
- Ensures consistency across Technical Assets

### Custom Mapping
This option allows you to override the default provisioning and specify your own technical identifiers. Use this when you need to:
- Integrate with existing infrastructure
- Follow specific naming requirements
- Provision resources outside standard conventions

**Important:** Custom mapping typically requires **explicit approval from a platform owner** before the Technical Asset can be provisioned. This additional review step ensures that custom configurations align with platform policies and don't conflict with existing resources.

**Recommendation:** Start with default mapping unless you have a specific requirement for custom configuration.

## Access modes

An admin can configure access modes for certain technical asset types.
When creating a technical asset with a type that has access modes enabled, the producer can choose which access modes to enable, or choose single access mode (meaning read only).

When granting access to a technical asset via an output port, the consumer must choose which access mode they want to use — but only when access modes are enabled for that technical asset.

Access modes are useful when a single technical asset supports multiple levels of access. For example, an API technical asset could define:

- **Basic**: Allows consumers to retrieve non-sensitive data through the API.
- **Admin**: Allows consumers to retrieve sensitive data through the API.

This could also be modelled as multiple Technical Assets, but that requires multiple Output Ports, which can become overwhelming for consumers. Access modes allow a single Output Port to cover these cases.

An Output Port can contain multiple assets with access modes enabled, but only when they share the same access modes.
If they differ, the producer must create multiple Output Ports.

## Representation
Within the Data Product Portal UI **Technical Assets** are always represented as **Squares**

![Data Output Example](./img/data-output.png)

---
