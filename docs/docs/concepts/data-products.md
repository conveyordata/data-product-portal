---
id: data-products
title: 🔵 Data Products
sidebar_position: 1
---

# 🔵 Data Products

**Data Products** are the fundamental building blocks of the Data Product Portal.
Their goal is to facilitate and simplify data management.

A Data Product can be thought of as a container that brings together people, technology and data.
It is governed and maintained by a group of people, who are responsible for assuring the quality of the product. 
A Data Product can consume data from other products through Input Ports, and expose data to other products via Output Ports.
Data does not exist in a void, but it is tied to certain storage infrastructure, and transformed through data pipelines defined in code.
These technical aspects are also governed by the Data Product concept.

## 🔍 Key Characteristics

- **Ownership**: Each data product has a clearly defined owner responsible for quality and compliance.
- **Autonomy**: Data products are independently deployable and testable.
- **Purpose-Driven**: Every data product serves a specific use case or business objective.
- **Lifecycle Managed**: From creation to deprecation, data products go through a full lifecycle.

## 🛠 What They Can Do

- Produce technical assets  (e.g. tables, APIs, files) that are exposed through **Output Ports**
- Register **Input Ports** by requesting access to the Output Ports of other products
- Implement fine-grained access control, observability, and versioning on these ports

## 📸 Example

A "Sales Transactions" data product may expose:
- A PostgreSQL table
- An S3 file export
- A REST API endpoint

These are all **Technical Assets** managed by the data product.
By default, all technical assets are private to the data product that manages them.
In order to share these assets with the outside world, they need to be exposed via an Output Port.

## Representation
Within the Data Product Portal UI **Data Products** are always represented as **Circles**

![Data Product Example](./img/data-product.png)

---
