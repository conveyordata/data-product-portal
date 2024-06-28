<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![APACHE License][license-shield]][license-url]


# Data Product Portal

[![Product Name Screen Shot][product-screenshot]](https://example.com)

The data product portal enables companies to build data products in a self-service way enabling analytics capabilities
for all departments/domains throughout an organisation. It introduces simple but powerful concepts that are easy to
understand and extensible to many types of data platform implementations. The data product portal can be considered as a
process tool that helps people working with data while also providing governance and insights how data is being used
throughout the organisation. The data product portal allows to build data products at scale by all departments/domains
in a self service manner while keeping control of how your data is being used.

The data product portal is agnostic to storage technologies (ie. AWS S3, Azure storage containers,… ) and data platforms
(AWS compute, Snowflake, Databricks,…) and abstracts away these technological challenges in a standardised way. The data
product portal offers a unified user experience that helps both people working on data products as people from the
business that need to keep oversight and control over how their data is being used in an organisation.

For companies that are struggling with enabling self service data product teams in their organisation to build data
products at scale, the data product portal provides a simple and understandable process that guides organisations
through all of the steps that come with building data products, it provides self-service and secure access to all of
the tools, data platforms, data sources and sharing concepts to all people building new data products. It keeps control
and oversight of all the data and data product development with the business stakeholders that are working with their
data. Unlike data catalogs like Collibra that focus mostly on describing your data, the data product portal guides you
through all the stages of the data product development cycle where all departments or domains can work on data products
in a governed and self service manner.

## Who is it for?

The Data Product Portal is aimed towards data teams in business who want to build their own use cases in a self-service
way, embracing data product thinking. The Data Product Portal automates away many of the steps you’re going to to get
onboarded on the data platform and start building data platforms.

The Data Product Portal needs support from your data platform team to be installed and integrated to their tooling. The
Data Product Portal is technology-agnostic. That means it can integrate with almost any cloud, with almost any tool and
with almost any dataset you might use. But you need to build those integrations once. We offer a few standard
integrations at launch, and we expect to extend this over time.

If you only have one data team or only a few use cases, the added overhead of setting up and managing the Data Product
Portal is probably too high. And it’s easier to manually configure each team and data product.

## Concepts
The data product portal guides product teams through all of the steps of the data product life cycle while taking into
account all governance aspects that are required from modern organisations. It does so by working around a couple of
simple concepts that provide data product teams in a self service way the capability to: Create new data products,
define who can work on them, request access to data sources, register new data sources for sharing, integrate with your
data platform seamlessly and do so while encouraging all best practices both from governance and engineering point of
view. With these concepts, the data product portal provides insights about what data products are out there, who is
using your data, for what reason and how your data flows through the organisation. At the same time it also provides
all practical tools and integrations for your data citizens to immediately start building data products in a safe and
governed environment using all the best practices.

The concepts we are introducing are:

- **Data product or project**: Data products are scoped data initiatives with a clear goal that different departments in
an organisation can work on to deliver business value. They are usually led by a data product owner that takes the
operational ownership of building, delivering and maintaining that data product and its data outputs for their
department or domain. Data product owners decide on the team that can work on that data product and requests access to
data sets that have been made available for sharing throughout the organisation. Data products typically follow the
data product lifecycle and the data product portal aims to guide the data product through the typical stages of the
data product lifecycle: From idea to experimentation to business validation to productisation to maintenance following
a governed, standardised and compliant process tailored to the needs of your organisation. All access, tooling and
interactions are configured and separated at the data product level, this means that people working on data products
can do so in a safe manner that does not have an impact on other data products. The automatic setup and configuration of
the data platforms of choice should be able to provide these guarantees.
- **Users**: Users are people that can work on a data product in a specific role. Users automatically get access to all
tooling and data sources based on the role they have for that data product. Depending on their permissions, they can
perform different actions like, interacting with development and/or production data, releasing data pipelines into
production, interact with schedulers, merge pull requests to master,… Users can work on multiple data products, but
never at the same time. Users always need to make a conscious choice of deciding of what data product they are working
for, as all permissions are set at the data product level and not at the user level. This has as an additional benefit
that you can guarantee that your data will always be used in the right context and that processing permissions and user
permissions are always aligned.
- **Datasets**: Datasets are a grouping of one or more data objects and are the level at which read data access is
granted to a data product. Datasets are owned by a data steward or other often business related person that can take
responsibility of approving access to specific data products. As data products have a specific scope and owner, it
becomes quite easy for dataset owners to assess whether access to their data is warranted. As access is granted to the
data product and not the user, the guarantee can be given that your data will only be usable for scope of the data
product that you approved access for. Only users that are allowed to work on a data product can interact with the tools,
services and data sources that are allowed for that data product.
- **Data objects**: Data objects are considered as the output of a data product. Data objects can be considered as files
on a storage location, tables in a database, topics on streaming queues,… Data objects are associated with a data
product that will (once approved) have full read and write permissions to those data objects in scope of the data
product. Data objects are never shared directly unless they are part of a dataset. This allows data product teams to
already work safely on their data objects or outputs, knowing that this will never be shared with anyone in the
organisation yet. You can register a data object to become a part of a dataset to make it shareable with the rest of the
organisation. During that registration process, the dataset owner can impose  guarantees to the data product team to
make sure that: Specific SLA’s are met, Data contracts/schemas are defined and guaranteed, data governance rules are
followed and the data catalog has been fed with the right information. This registration of data objects to a dataset
can be very flexible and adapted to the needs of the organisation.

With these simple principles we can solve a lot of questions that companies are facing for people working with data
as well as for people that keep oversight and are concerned with governance aspects.

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

[stars-shield]: https://img.shields.io/github/stars/conveyordata/data-product-portal.svg?style=for-the-badge

[stars-url]: https://github.com/conveyordata/data-product-portal/stargazers

[issues-shield]: https://img.shields.io/github/issues/conveyordata/data-product-portal.svg?style=for-the-badge

[issues-url]: https://github.com/conveyordata/data-product-portal/issues

[license-shield]: https://img.shields.io/github/license/conveyordata/data-product-portal.svg?label=license&style=for-the-badge

[license-url]: https://github.com/conveyordata/data-product-portal/blob/master/LICENSE.md

[product-screenshot]: images/screenshot.png
