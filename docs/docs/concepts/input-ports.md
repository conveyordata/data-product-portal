---
id: input-ports
title: Input Ports
sidebar_position: 5
---

# Input Ports

**Input Ports** are logical counterparts of **[Output Ports](./output-ports)**.
Their function is to record and facilitate access to the data of other products.
Both **[Data Products](./data-products)** and **[Explorations](./explorations)** can have Input Ports.

## What’s in an Input Port?

An Input Port is a relatively lightweight concept.
It mainly exists to establish a link between a consuming **[Data Product](./data-products)** or **[Exploration](./explorations)**, and the **[Output Port](./output-ports)** of the producing **[Data Product](./data-products)**.
As such, the Input Port contains the "data agreement" for this link:
what is the justification for accessing this data, for what period of time, who were the requesting and approving parties, ...

## Access Management

Input Ports allow tracking the consumers of a certain **[Output Port](./output-ports)**.
By listing all the consuming Input Ports, an Output Port owner can easily track the usage of their assets.
The owner of the data always stays in control, and can revoke access by unlinking an Input Port connected to their Output Port.

---
