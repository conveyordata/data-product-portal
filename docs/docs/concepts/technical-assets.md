---
id: technical-assets
title: 🟦 Technical Assets
sidebar_position: 2
---

# 🟦 Technical Assets

**Technical Assets** are the individual data entities that are managed by a Data Product.
They represent the actual, physical data that is owned by a Data Product.

## 🔧 Examples

- An S3 path (e.g. `s3://sales-data/transactions/2024/`)
- A table in a database (e.g. `analytics.sales_transactions`)
- A Kafka topic (e.g. `sales-events-stream`)
- A REST API (`GET /sales/transactions`)

## 🔐 Governance

Each Technical Asset is registered, versioned, and described with:
- Access control rules
- Technical schema and metadata
- Ownership information

Consumers cannot access these assets directly.
Instead, Data Products offer Output Ports, which bundle a collection of related assets together to provide managed read access.
Output Ports should follow the advice that data that belongs together should also be shared together.

## Representation
Within the Data Product Portal UI **Technical Assets** are always represented as **Squares**

![Data Output Example](./img/data-output.png)

---
