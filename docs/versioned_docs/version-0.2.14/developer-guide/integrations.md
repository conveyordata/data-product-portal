---
id: integrations
title: Data Platform Integrations
sidebar_label: Integrations
sidebar_position: 5
---

# Data Product Portal Sample Implementations

The Data Product Portal helps you organize the process of building data products at scale in a self-service manner.

Most organizations leverage cloud data platform technologies like **AWS**, **Azure**, **Databricks**, **Snowflake**, etc., and this portal integrates with those platforms to streamline development workflows and governance.

![A high-level representation of how to integrate the Data Product Portal](./img/img.png)

---

## Overview

This section describes how to integrate the portal with your platform of choice. The [`integrations`](./integrations) folder provides **sample implementations** that translate portal configurations into:

- Data access configuration
- Platform tooling setup
- User permission mapping
- Data product lifecycle automation

### Currently Supported Integrations

- **AWS**: S3, Glue, Athena *(Redshift Serverless coming soon)*
- **Conveyor**: A self-service workflow manager for data products

### Upcoming Integrations

- **Cloud Platforms**: Databricks, Snowflake, Azure
- **Data Catalogs**: Amundsen, DataHub, Collibra

If there's a platform you want us to support, let us know — or better yet, open a PR!

---

## AWS Mapping

Here's how the core concepts of the Data Product Portal map to AWS resources:

| Portal Concept     | AWS Resource(s) |
|--------------------|-----------------|
| **Data Environments** | S3 buckets, Glue databases/tables |
| **Data Products**      | IAM roles/policies granting scoped access to S3 and Glue |
| **Datasets**           | Groups of S3 paths and Glue tables |
| **Data Outputs**       | Shareable outputs: S3 paths, Glue tables, Athena queries |
| **Users**              | Access is managed via IAM roles and policies provisioned by the portal |

---

## Conveyor Mapping

| Portal Concept     | Conveyor Resource |
|--------------------|-------------------|
| **Data Environments** | Conveyor environments (execution isolation) |
| **Data Products**      | Conveyor projects (build, deploy, run workflows) |
| **Users**              | Portal-managed access to Conveyor projects and datasets |

The portal manages the mapping of users to Conveyor roles through its UI and API.

---

## Terraform Integration

Infrastructure configuration and provisioning are handled via **Terraform**.

### Integration Flow

1. **Configure Terraform**: Set up your provider and initial variables.
2. **Run Terraform**: Use the sample config files to provision resources.
3. **Pull Configs from Portal**: Retrieve generated config files from the Data Product Portal.
4. **Update Terraform**: Feed those configs back into your Terraform setup.

📄 More details in the [`terraform/README.md`](https://www.github.com/conveyordata/data-product-portal/tree/main/integrations/terraform/README.md)

---
