# Consumption of Data by Dashboards, Applications and End Users

**Status:** Proposed. Up for a team vote between the three options.

## Context and Problem Statement

Portal models two things that hold an Input Port on an Output Port: a Data Product and an Exploration ([ADR-0016](./0016-light-weight-data-products.md)).
A person never holds an Input Port; a person requests one on behalf of a Data Product or an Exploration.

Many consumers produce nothing: a Power BI dashboard for a team, an organisation-wide report, an application or an AI agent, an integration that moves data to another system.
The people who read a dashboard (end users) have no place in Portal.
They cannot discover a dashboard, ask to see it, or be granted the data it shows.

How a dashboard reads its data decides who needs access:

| | Technical identity | Viewer identity |
|---|---|---|
| The dashboard reads with | Its own identity, such as a service principal | The identity of each person viewing it, such as Power BI single sign-on to Databricks |
| Needs a grant on the data | Only the dashboard's identity | Every reader |
| What a reader sees | What the dashboard shows | What their own grants allow, with the data platform's row filters and column masks |

The question is where a dashboard or application lives in Portal, and how its readers get access.

## Decision Drivers

1. Both technical identity and viewer identity work.
2. Every reader has a stated purpose and someone who answers for the access.
3. End users discover a dashboard in Portal and request access to it.
4. The Output Port owner sees who reads their data and can revoke the access.
5. It scales to large Groups of readers that change often.
6. It adds as few concepts as possible.

## Scenarios

| Scenario | Description |
|---|---|
| Team dashboard on own data | The team that owns a Data Product builds a dashboard on its own data. |
| Organisation-wide dashboard | About 500 readers who don't know each other and come and go. |
| Dashboard by another team | A team builds a dashboard on data owned by other teams. |
| Combining Data Products | A dashboard that reads Output Ports of several Data Products. |
| Different views | One dashboard where some readers see personal data or only their own region. |
| Application, agent or integration | An app or agent used by end users, or an integration that moves data to another system with a service principal. |

## Considered Options

* **Option 1: Consumption as a separate concept.** A Consumption sits next to Data Product and Exploration. It holds Input Ports, its Technical Assets are the dashboards and apps, and audiences decide who opens which Technical Asset. Its owner may differ from the owners of the data. Every new reader who joins an audience gives a business justification, and the Consumption owner approves.
* **Option 2: Dashboard as an Output Port, readers through Explorations.** A dashboard or app is an Output Port of the Data Product that builds it. Its access modes map to the tool's audiences and row-level security. A reader, or a Group, requests it through an Exploration. The business justification is given once, for the Exploration; members of its Group come and go without one.
* **Option 3: Audiences on a Data Product.** A Data Product has audiences next to its Output Ports. An audience holds members and the Technical Assets they open. The audience is always owned by the Data Product's owner. Every new reader who joins an audience gives a business justification, and the Data Product owner approves.

The options differ on three points:

* **Who owns the readers.** In Option 2 the reader asks through the existing request flow. In Options 1 and 3 the owner of the dashboard manages an audience.
* **How often a reader justifies access.** In Option 2 once per Exploration, which can cover a whole Group. In Options 1 and 3 once per reader, so the owner sees a justification for every new reader.
* **Different owners without a Data Product.** Only Option 1 lets a team own a dashboard on other teams' data without creating a Data Product for it.

## Comparison per scenario

| Scenario | Option 1: Consumption | Option 2: Output Port and Explorations | Option 3: Audiences on a Data Product |
|---|---|---|---|
| Team dashboard on own data | A Consumption next to the Data Product; its Input Ports are approved automatically | An Output Port on the own Data Product | An audience on the own Data Product |
| Organisation-wide dashboard | Readers join an audience; the Consumption owner approves | One Exploration per reader or Group; the Output Port owner approves | Readers join an audience; the Data Product owner approves |
| Dashboard by another team | A Consumption owned by that team | That team creates a Data Product for the dashboard | Same as Option 2 |
| Combining Data Products | Input Ports on several Output Ports | Through the dashboard's own Data Product | Same as Option 2 |
| Different views | One Technical Asset per view, or viewer identity | One access mode per view, mapped to the tool's audiences and row-level security | One audience per view, each with its own Technical Assets |
| Viewer identity | Readers get the grants of the Input Ports their Technical Asset reads | The Provisioner grants readers the data the dashboard reads | Readers get grants on data inside the Data Product |
| Application, agent or integration | A Consumption whose Technical Asset reads with a machine user | An app or API is an Output Port; an integration is an Exploration owned by a machine user | A machine user in an audience |
| Business justification | Per reader who joins an audience | Once per Exploration, covering every member of its Group | Per reader who joins an audience |
| New concepts | Consumption and audience | None | Audience |

## Decision Outcome

Open for the team vote.

## Pros and Cons of the Options

### Option 1: Consumption as a separate concept

* **Good, because** a team can own a dashboard or app on other teams' data, from several Data Products, without a Data Product of its own.
* **Good, because** the Output Port keeps meaning data that others build on.
* **Bad, because** it is a new concept in the domain, the UI, authorization and the provisioning events.
* **Bad, because** a producer that builds a dashboard on its own data manages a Data Product and a Consumption.
* **Bad, because** it sits close to the Exploration and makes the difference between the two harder to explain.

### Option 2: Dashboard as an Output Port, readers through Explorations

* **Good, because** it adds no concept: dashboards and APIs are Output Ports, and readers use the request flow and marketplace that exist.
* **Good, because** access modes give one dashboard different views, the same way for dashboards and APIs.
* **Bad, because** an Output Port is no longer only data that others build on, so Portal has to stop Data Products from requesting a dashboard.
* **Bad, because** Explorations need a Group as requester and a request light enough to start from an "add reader" button. Access duration per requester is already an admin setting, so readers can get permanent access.
* **Bad, because** the name "Exploration" reads as a step towards a Data Product rather than a request for access with a reason, so the concept has to be renamed in the code, the UI, the API and the docs.
* **Bad, because** an Exploration cannot consume an Invite only Output Port, so sensitive dashboards need that rule revisited.
* **Bad, because** with viewer identity the Provisioner grants readers the data behind the dashboard, which is not the Output Port they requested.

### Option 3: Audiences on a Data Product

* **Good, because** the producer shares a dashboard from its own Data Product without another concept to request through.
* **Bad, because** the producer manages and approves every reader.
* **Bad, because** with viewer identity readers get grants on data inside the Data Product, close to what it never publishes.
* **Bad, because** a team that only builds a dashboard needs a Data Product, as in Option 2.

## Open Questions

1. **What an Exploration is.** Its purpose, its name, a Group as requester, and creating one behind an "add reader" button. This may need its own ADR.
2. **Grants under viewer identity.** How the Provisioner grants readers the data a dashboard reads, and how the Output Port owner sees that.
3. **Kinds of Output Port.** Which requesters may request which kind of Output Port, if dashboards and apps become Output Ports.
4. **Moving a Technical Asset.** In Option 1, a dashboard a team built inside its Data Product is rebuilt in a Consumption once others need it. Should Portal move the Technical Asset instead, keeping the underlying resource?
5. **Name.** "Consumption" is a working name for Option 1. See Appendix A for how other tools and open standards name it.

## Appendix A: How others name it

None of the open standards has an entity for the thing that consumes; they describe the producing side.

| Source | Name | Notes |
|---|---|---|
| [dbt](https://docs.getdbt.com/docs/build/exposures) | Exposure | "A downstream use of your dbt project". Types: dashboard, notebook, analysis, ml, application. Metadata only. |
| [Collibra](https://productresources.collibra.com/docs/collibra/latest/Content/Catalog/DataSets/ta_request-access-to-data-set.htm) | Data Usage | Created by an access request; holds the assets, purpose and dates. |
| [DataHub](https://docs.datahub.com/docs/generated/metamodel/entities/dashboard) | Dashboard, Chart | One entity per kind, linked to data by "Consumes". |
| [Purview](https://learn.microsoft.com/en-us/purview/concept-data-products) | Subscribers, use cases | Subscribers of a data product; the data product lists use cases. |
| Delta Sharing | Recipient | The identity that receives a share. |
| Power BI | App, Audience | An app has audiences of readers. |
| [Bitol ODPS](https://github.com/bitol-io/open-data-product-standard/blob/main/schema/odps-json-schema-latest.json) | `usage` | Input, output and management ports; "Recommended usage of the data". |
| [Bitol ODCS](https://github.com/bitol-io/open-data-contract-standard/blob/main/docs/roles.md) | consumer | A party; `roles` lists the roles a consumer needs, with approvers. |
| [Open Data Mesh DPDS](https://github.com/opendatamesh-initiative/odm-specification-dpdescriptor/blob/main/versions/1.0.0-DRAFT.md) | `audience`, `usage` | Expectations a port declares about who uses it and how. |
| [Open Data Product Specification](https://opendataproducts.org/v4.0/) | `useCases` | Use cases of a data product; AI agents as an access type. |
