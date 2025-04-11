---
id: installation
title: Installation Guide
description: How to install and run the Data Product Portal
sidebar_position: 2
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Data Product Portal Installation Guide

_Your gateway to installing and running the Data Product Portal in various environments._

## Quick Start

For an easy way to get started in under 5 minutes, please head over to the [Quickstart](./quickstart) page

---

## Production Installation

The portal consists of two main services:
- A **backend**
- A **frontend**

Both are available as Docker images and can be deployed in Kubernetes via our Helm chart.

### Helm Chart

A public Helm chart is available:

```bash
public.ecr.aws/conveyordata/data-product-portal
```

Update your `values.yaml` to match your environment. By default, images will use the appropriate tag for the chart version — **do not override unless necessary**.

#### Database

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
- A configured OIDC provider (e.g., AWS Cognito)
- Client ID and secret

Linking with OIDC is recommended. If OIDC is not configured all of the users will be authenticated as the default *John Doe* making actual use cases very difficult.

#### API keys
If you enable the `api_key` in the `values.yaml` and pass a `key` you define it is possible to connect to the API with this key. This key has full admin access. Use it wisely.

#### Conveyor

To enable Conveyor integration:
- Pass your **Conveyor API key and secret** in `values.yaml`
- Ensure the keys belong to a **CI/CD system user**

#### CLI

A standalone CLI tool is available for interacting with the portal. You can find the executable and instructions in the CLI documentation.

---

## Local Developer Set-up

For local development:
- Have a look at the [developer documentation](../developer-guide/setup).
- Refer to the individual folder `README.md` files in the repository.
- These contain setup and contribution instructions for the backend and frontend codebases.

---

Need help? Reach out to the team or check our [FAQ](../faq).
