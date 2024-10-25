<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![APACHE License][license-shield]][license-url]
[![OpenSSF Scorecard][scorecard-shield]][scorecard-url]


# Data Product Portal

[![Product Name Screen Shot][product-screenshot]](https://raw.githubusercontent.com/conveyordata/data-product-portal/main/images/screenshot.png)

## Introduction

The Data Product Portal enables to **_scale_** building data products across all departments in an organisation in a
**_self-service_** manner. It does so by providing a guided setup for creating data products, with proper approval processes
that will **_enable governance by design_** for data initiatives. The portal is a process tool that helps data professionals
do their work more efficiently while providing governance and insights into how data is being used throughout the organisation.

Unlike traditional data catalogs that primarily focus on describing data, the Data Product Portal guides you through
the entire data product development lifecycle. This includes self-service and secure access to tools, data platforms,
data sources, and sharing concepts, ensuring control and oversight for business stakeholders.

Our goal is to bridge the gap between data governance, data platforms and data catalogs and provide a 360 view of all
ongoing data initiatives that is easy to understand by everybody.

To read more about it, please checkout our [announcement blogpost](https://hubs.li/Q02DGGpR0)

## Who is it for?

The Data Product Portal is designed for data teams within businesses that aim to build their own use cases in a
self-service way, embracing data product thinking. It automates many of the onboarding steps required to start building
data platforms.

While the portal is technology-agnostic and can integrate with various clouds, tools, and datasets, it requires initial
support from your data platform team for installation and integration. We offer several standard integrations at launch
and plan to extend these over time.

If your organization has only one data team or a limited number of use cases, the data product portal might not be
something for you. With the data product portal we aim to help organisations that want to scale building data products
by offering self-service capabilities.

## Concepts

The Data Product Portal guides product teams through the data product life cycle, considering all governance aspects
required by modern organizations. It introduces several key concepts:

### Data Products

A data product is a scoped data initiative with a clear goal, led by a data product owner. The owner manages the team,
requests access to datasets, and follows a governed, standardized, and compliant process tailored to the organization’s
needs. All access, tooling, and interactions are configured at the data product level, ensuring safe and isolated
development.

### Users

Users are individuals who work on a data product in specific roles, gaining access to tools and data sources based on
their roles. They perform various actions such as interacting with data, releasing pipelines, and merging pull requests.
Users can work on multiple data products but must choose which one they are working on at any given time, ensuring data
is used in the right context.

### Datasets

Datasets group one or more data outputs and are the level at which read data access is granted to a data product.
Dataset owners, typically business-related individuals, approve access to specific data products. Access is granted to
data products rather than users, guaranteeing that data is used only for the approved scope.

### Data Outputs

Data outputs are outputs of a data product, such as files, tables, or topics. They are associated with a data product
that has full read and write permissions. Data outputs are never directly shared unless they are part of a dataset,
allowing safe development until they are ready for organizational sharing.

## Benefits

Adopting the Data Product Portal offers several benefits:
- **Guided Setup:** Step-by-step assistance involving the right stakeholders for creating data products, requesting
access, adding users and registering new data for sharing with other data products.
- **Governance by Design:** Ensures that data products are compliant with the organization’s data governance policies and
standards, with proper approval processes and access controls.
- **Scale across the organization:** Enables all departments to start new data initiatives easily without having to depend on
a central team.
- **Tech Translation:** Converts high-level concepts into specific configurations settings for platforms like AWS,
Azure, Databricks, Snowflake, and others, making sure that each data product is correctly separated and not impacting
each other.
- **User-Friendly Interface:** Makes it easy for business users and people working with data to understand and navigate
the data landscape.
- **Self-service:** Enables departments and teams to start new data initiatives easily without having to depend on a
central team. 
- **Comprehensive Overview:** Combines data catalogs, data platforms and data governance aspects into a single 360
overview of all ongoing data initiatives.

# Additional resources

## General Blogposts

- [Announcement Blogpost](https://medium.com/conveyordata/introducing-data-product-portal-an-open-source-tool-for-scaling-your-data-products-c05cf86afbf4)
- [Interface to your data platform](https://medium.com/conveyordata/build-an-interface-to-your-data-platform-f1927c33c5ad)
- [State of data products](https://medium.com/conveyordata/the-state-of-data-products-9e1bc5c39bcb)
- [How to effectively structure data for self service data teams](https://medium.com/conveyordata/how-to-effectively-structure-data-for-self-service-data-teams-09c6d48f3beb)

## Technical Blogposts

- [Data product integrations: OIDC](https://medium.com/conveyordata/data-product-portal-integrations-1-oidc-8d1dcdc0896e)
- [Data product integrations: Helm and Kubernetes](https://medium.com/conveyordata/data-product-portal-integrations-2-helm-982f4a54c0f0)
- [Data product integrations: Data platforms](https://medium.com/conveyordata/data-product-portal-integrating-with-your-data-platform-41bf9fcf1fc1)
- [Data product integrations: AWS](https://medium.com/conveyordata/data-product-portal-integrating-with-your-data-platform-41bf9fcf1fc1)

# Getting Started

## Local Sandbox

### Prerequisites

#### Docker

- Install [Docker](https://docs.docker.com/get-docker/) on your machine.

### Installation
- Ensure your Docker service is running.

- In order to set up a local 'production-like' server with a connection to a database, run the command below in the root of this project.
  ```sh
  docker compose up
  ```

- If you want to make sure recent changes in the repository are reflected, run the command below instead.
  ```sh
  docker compose up --build
  ```
- Now visit http://localhost:8080 to check it out!

### Sample Data
While running in sandbox mode, the Portal will be automatically seeded with sample data (incl. users, data products, datasets, ...). The source of this data can be found in the [sample_data.sql](./backend/sample_data.sql) file.
If you want to see different data in the sandbox mode, you can either modify this file or create your custom data file and reference that one in the [compose.yaml](compose.yaml) instead of the 'sample_data.sql' file. See the comments to learn how to pass a local file to that container.

### Limitations

The default local sandbox is [configured](.env.docker) to *disable OAuth* and to *disable AWS calls*. This allows for a
very easy first-time setup that will give you a quick overview of the functionality the Data Product Portal provides. If
you want to explore additional technical integrations, more setup is required (see below).

## Local Development

### Prerequisites

#### Pre-commit hooks
It is recommended that you enable the pre-commit hooks the moment you start contributing to the project.

- Install pre-commit ([pip](https://pre-commit.com) / [brew](https://formulae.brew.sh/formula/pre-commit)) on your machine.
- Run the command below in the root of this project.
```sh
pre-commit install
  ```

### Backend

For backend specific instructions, check [backend/README.md](backend/README.md)

### Frontend

For frontend specific instructions, check [frontend/README.md](frontend/README.md)

# Integrations
The data product portal comes with default integrations for many different platform technologies. Check out the
[integrations](integrations/README.md) folder for more information. These integrations are meant as an example on how
you can translate the data product portal configuration to a practical implementation for your data platform.

![Integrating portal with your data platform](images/img.png)

Right now we support the following integrations:
- **AWS**: S3, Glue, Athena, (Redshift serverless coming soon)
- **Conveyor**: A data product workflow manager that helps you build data products in a self-service manner

A more detailed explanation of how to integrate the data product portal with your data platform can be found in our
[platform integration blogpost](https://medium.com/conveyordata/data-product-portal-integrating-with-your-data-platform-41bf9fcf1fc1).

We are currently working on Databricks and Snowflake integrations and more are to come soon. If you have a specific
request for a technology integration, please don't hesitate to reach out to us. Even better would be to create a pull
request with the integration you would like to see in the data product portal.

# Production Installation
Please find the relevant info in [Installation](docs/INSTALLATION.md)

# Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any
contributions you make are **greatly appreciated**.

Check our [Contributing Guidelines](CONTRIBUTING.md).

# License

Distributed under the APACHE 2.0 License Copyright 2024 Dataminded. See [LICENSE](LICENSE.md) for more information.

# Contact

Email: [info@dataminded.com](mailto:info@dataminded.com)

Project Link: [https://github.com/conveyordata/data-product-portal](https://github.com/conveyordata/data-product-portal)

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/conveyordata/data-product-portal.svg?style=for-the-badge

[contributors-url]: https://github.com/conveyordata/data-product-portal/graphs/contributors

[forks-shield]: https://img.shields.io/github/forks/conveyordata/data-product-portal.svg?style=for-the-badge

[forks-url]: https://github.com/conveyordata/data-product-portal/network/members

[scorecard-shield]: https://img.shields.io/ossf-scorecard/github.com/conveyordata/data-product-portal.svg?style=for-the-badge

[scorecard-url]: https://img.shields.io/ossf-scorecard/github.com/conveyordata/data-product-portal

[stars-shield]: https://img.shields.io/github/stars/conveyordata/data-product-portal.svg?style=for-the-badge

[stars-url]: https://github.com/conveyordata/data-product-portal/stargazers

[issues-shield]: https://img.shields.io/github/issues/conveyordata/data-product-portal.svg?style=for-the-badge

[issues-url]: https://github.com/conveyordata/data-product-portal/issues

[license-shield]: https://img.shields.io/github/license/conveyordata/data-product-portal.svg?label=license&style=for-the-badge

[license-url]: https://github.com/conveyordata/data-product-portal/blob/master/LICENSE.md

[product-screenshot]: images/screenshot.png
