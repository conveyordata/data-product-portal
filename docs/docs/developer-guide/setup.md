---
id: setup
title: Local developer setup
description: How to setup your environment for local development
sidebar_position: 1
---

## Prerequisites

### Pre-commit Hooks

To ensure consistent code quality, it's recommended to enable pre-commit hooks early when contributing.

1. Install [`pre-commit`](https://pre-commit.com) using [pip](https://pre-commit.com/#install) or [brew](https://formulae.brew.sh/formula/pre-commit)
2. Run the following command in the root of the project:

```bash
pre-commit install
```

---

## Backend Setup

See the [backend](./backend) for backend-specific setup and instructions.

---

## Frontend Setup

See the [frontend](./frontend) for frontend-specific instructions.

---

# Integrations

The Data Product Portal ships with default integrations for many modern platform technologies.

For details, check the [integrations](./integrations) documentation.

These integrations demonstrate how to translate the portal configuration into real implementations for your data platform.

## Current Integrations

- **AWS**: S3, Glue, Athena *(Redshift Serverless coming soon)*
- **Conveyor**: A workflow manager for building data products with self-service

📝 Check out our full write-up on platform integration in this blog post:

👉 [How the Portal Integrates with Data Platforms](https://conveyordata.com/portal-how-portal-integrates-with-data-platforms?utm_source=github-portal-readme&utm_medium=referral)

---

## Upcoming & Community Integrations

We’re working on:

- **Databricks**
- **Snowflake**

Have a request? Let us know — or even better, open a pull request to contribute an integration you'd like to see!
