---
id: installation
title: Installation Guide
description: How to install and run the Data Product Portal
sidebar_position: 2
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Installation Guide

In this guide we describe how to install Portal in a production like environment.
If your goal is to quickly try out portal locally, take a look at our [local setup](../getting-started/installation.md)

## Production Installation

The portal consists of two main services:
- A **backend**
- A **frontend**

Both are available as Docker images and can be deployed in Kubernetes via our Helm chart.

### Helm Chart

A code of the Helm chart is available [here](https://github.com/conveyordata/data-product-portal/tree/main/helm) and the chart is hosted at:

```bash
public.ecr.aws/conveyordata/data-product-portal
```

Update your `values.yaml` to match your environment. By default, images will use the appropriate tag for the chart version — **do not override unless necessary**.

#### Database

:::warning

We use PGVector to empower search functionality in Portal.
Most cloud vendors do support PGVector so it's most likely not an issue.

:::

- **Preferred**: Use an external managed database like AWS RDS.
- **Alternative**: Use the bundled PostgreSQL Helm dependency for in-cluster setup. By default this in-cluster database is *disabled*.

#### Host

A dedicated hostname is required for running a production setup of Portal.
Both the backend and the frontend components need this as an environment variable to ensure communication between the services is possible.
Adjust the **host** value in the `values.yaml`

#### Ingress

Ingress is enabled by default. You must provide correct annotations for your platform (e.g., AWS Load Balancer Controller).

#### Service Account

A default Kubernetes service account is included.
To enable **AWS integrations**, link this with **IRSA** ([IAM Roles for Service Accounts](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html)).

#### OIDC

Enable OIDC by supplying credentials via `values.yaml`. You’ll need:
- A configured OIDC provider (e.g., [AWS Cognito](https://aws.amazon.com/cognito/))
- Client ID and secret

Linking with OIDC is recommended. If OIDC is not configured all users will be authenticated as the same user.
This user can be configured using the environment variable `DEFAULT_USERNAME`.
When not specified, the default user is *john.doe@pharma.com*.

#### API keys
If you enable the `api_key` in the `values.yaml` and pass a `key` you define it is possible to connect to the API with this key. This key has full admin access. Use it wisely.

#### Conveyor

To enable Conveyor integration:
- Pass your **Conveyor API key and secret** in `values.yaml`
- Ensure the keys belong to a **CI/CD system user**

#### CLI

A standalone CLI tool is available for interacting with the portal. You can find the executable and instructions in the CLI documentation.
