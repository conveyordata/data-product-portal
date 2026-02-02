# Select a Standard for Defining Data Products as Code

## Context and Problem Statement

Portal needs a single, industry-standard specification that allows customers to manage Data Products as Code.
This enables syncing data product updates as part of a CI/CD pipeline.
This specification must describe a full data product, not just a data contract, and must be suitable for long-term maintenance, automation, and industry alignment.

## Decision Drivers

* Industry adoption and market credibility
* Ability to represent a full data product
* Compatibility with Portal’s domain model
* Suitability for managing Data Products as Code

## Considered Options

* **Option 1**: [DPDS](https://dpds.opendatamesh.org/) (Open Data Mesh)
A comprehensive, enterprise-grade specification promoted by the Open Data Mesh community.
* **Option 2**: [BiToL Open Data Product Standard](https://bitol-io.github.io/open-data-product-standard/latest/)
A developer-centric, YAML-based standard designed explicitly for defining data products as code.
* **Option 3**: [Data Product Specification](https://dataproduct-specification.com/) created by the people of the data mesh manager
* **Option 4**: Other standards (ProMoTe, dprod, Open Data Products)
A set of alternative specifications with narrower scope, lower adoption, or architectural misalignment.

## Decision Outcome

**Chosen option**: *BiToL Open Data Product Standard*

BiToL was selected because it provides full data product coverage while remaining simple, human-readable, and automation-friendly.
It aligns strongly with the “data product as code” philosophy, making it the best fit for Portal’s target users and architecture.
BiToL will be documented as the single supported standard for data product specification.

An example illustrating the use of the BiToL data product specification can be found:
- [data product specification](https://github.com/conveyordata/data-product-portal/blob/main/integrations/bitol/data-product-example.yml).
- [data contract specification](https://github.com/conveyordata/data-product-portal/blob/main/integrations/bitol/data-contract-example.yml).

## Pros and Cons of the Options

### Option 1: DPDS (Open Data Mesh)

* Good, because it is widely adopted and positioned as the market leader in enterprise data mesh specifications.
* Neutral, because it supports full data product concepts but assumes a highly opinionated enterprise operating model.
* Bad, because it is very verbose, rigid, and complex.

### Option 2: Bitol Open Data Product Standard

* Good, because it is designed explicitly for defining data products as code and uses a simple YAML structure.
* Good, because it was built using a developer-first mentality.
* Good, because its model aligns well with the existing Portal concepts
* Neutral, because some governance and lifecycle aspects may require additional Portal conventions.

### Option 3: Data product specification

* Good, because it was built using a developer-first mentality.
* Good, because it is designed explicitly for defining data products as code and uses a simple YAML structure.
* Bad, as it is EOL and the people from data mesh manager are also
  [migrating to the Bitol standard](https://www.linkedin.com/posts/simonharrer_industry-first-entropy-data-launches-activity-7381248666382004224-OBOS).

### Option 4: Other Standards

* Bad, lack of full data product coverage
* Bad, lack of adoption in the market
