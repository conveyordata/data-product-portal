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
oci://public.ecr.aws/conveyordata/helm
```

Update your `values.yaml` to match your environment. By default, images will use the appropriate tag for the chart version — **do not override unless necessary**.

#### Database

Requirements:
- Postgres version 17 or higher
- PGVector extension available, minimum version 0.8.0. This is supported by most cloud vendors ([AWS](https://docs.aws.amazon.com/AmazonRDS/latest/PostgreSQLReleaseNotes/postgresql-extensions.html#postgresql-extensions-17x), [Azure](https://learn.microsoft.com/en-us/azure/postgresql/extensions/concepts-extensions-versions#vector) and [GCP](https://docs.cloud.google.com/sql/docs/postgres/extensions#miscellaneous-extensions).

We recommend using a managed database service.

The backend logs in to the database in one of two ways, set with `POSTGRES_AUTH_MODE`:

| Setting | Default | Meaning |
|---|---|---|
| `POSTGRES_AUTH_MODE` | `password` | `password` sends `POSTGRES_PASSWORD`. `azure` asks Microsoft Entra ID for a short-lived token for every new connection and sends that as the password. |
| `POSTGRES_PASSWORD` | | Required with `password`. Leave it empty to let the database driver read the password from the file in `PGPASSFILE`. Not used with `azure`. |
| `AZURE_CLIENT_ID` | | Only with `azure`. The client id of the user-assigned managed identity to log in with, when the host has more than one. This is the standard Azure SDK variable; AKS workload identity sets it for you. |

For Azure Database for PostgreSQL with Entra ID authentication, set `POSTGRES_USER` to the name of the managed identity's database role and use:

```
POSTGRES_AUTH_MODE=azure
PGSSLMODE=require
```

In the Helm chart these are `database.auth_mode` and `database.sslmode`.

For other token sources, such as HashiCorp Vault or a cloud IAM sidecar, let them write the password to a [password file](https://www.postgresql.org/docs/current/libpq-pgpass.html), point `PGPASSFILE` to it and leave `POSTGRES_PASSWORD` empty. The driver reads the file for every new connection, so a refreshed password is picked up without a restart.

`AZURE_CLIENT_ID`, `PGSSLMODE` and `PGPASSFILE` are read by the Azure SDK and the database driver, not by the portal, so set them as environment variables of the backend container. A `.env` file does not reach the driver.

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
