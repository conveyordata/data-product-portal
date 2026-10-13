---
id: data-products
title: Data Products
sidebar_position: 1
---

# Data Products

**Data Products** are the fundamental building blocks of the Data Product Portal.
Their goal is to facilitate and simplify data management.

A Data Product can be thought of as a container that brings together people, technology and data.
It is governed and maintained by a group of people, who are responsible for assuring the quality of the product.
A Data Product can consume data from other products through **[Input Ports](./input-ports)**, and expose data to other products via **[Output Ports](./output-ports)**.
Data does not exist in a void, but it is tied to certain storage infrastructure, and transformed through data pipelines defined in code.
These technical aspects are also governed by the Data Product concept.

## Key Characteristics

- **Ownership**: Each Data Product has a clearly defined owner responsible for quality and compliance.
- **Autonomy**: Data products are independently deployable and testable.
- **Purpose-Driven**: Every Data Product serves a specific use case or business objective.
- **Lifecycle Managed**: From creation to deprecation, Data Products go through a full lifecycle.

## What They Can Do

- Produce [Technical Assets](./technical-assets) (e.g. tables, APIs, files) that are exposed through **[Output Ports](./output-ports)**
- Register **[Input Ports](./input-ports)** by requesting access to the **[Output Ports](./output-ports)** of other Data Products
- Implement fine-grained access control, observability, and versioning on **[Output Ports](./output-ports)**

## Environments

Each Data Product stores its environments and the date each was declared. Technical Assets and Output Ports inherit that scope.

When creating a Data Product, the environment selector starts with the global defaults. You can select one or more environments from the configured catalogue. Once a Data Product is created, its selected environments can no longer be removed; edits can only add new ones. The detail pages of Data Products, Technical Assets, and Output Ports show the declared environments as read-only tags.

The API accepts `environment_ids` when creating or updating a Data Product. If omitted during creation, the current global environments are saved as defaults. Changing globals or moving the Data Product to another Domain does not change its saved environments. Updates can add environments, but cannot remove existing ones or save an empty selection.

Domains do not configure environments. During the upgrade, legacy Domain selections (or global defaults when no selection existed) are copied into Data Product declarations before Domain environment settings are removed. Existing Data Product declarations are preserved.

Environments must be configured before creating a Data Product. During an upgrade, every existing Data Product must have at least one effective environment, either through its Domain or the global defaults. The migration stops with a configuration error otherwise. See [Environment setup](../developer-guide/adding-integrations.md#environment-setup) for installations that do not have environments configured yet.

## Example

A "Sales Transactions" Data Product may expose:
- A PostgreSQL table
- An S3 file export
- A REST API endpoint

These are all **[Technical Assets](./technical-assets)** managed by the Data Product.
By default, all Technical Assets are private to the Data Product that manages them.
In order to share these assets with the outside world, they need to be exposed via an **[Output Port](./output-ports)**.

## Representation
Within the Data Product Portal UI **Data Products** are always represented as **Circles**

![Data Product Example](./img/data-product.png)

---
