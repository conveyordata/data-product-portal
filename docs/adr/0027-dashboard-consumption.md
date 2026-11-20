# Consumption of Data by Dashboards, Applications and End Users

**Status:** Proposed. Up for a team vote between the three options.

## Context and Problem Statement

Portal models two things that hold an Input Port on an Output Port: a Data Product and an Exploration ([ADR-0016](./0016-light-weight-data-products.md)).
A person never holds an Input Port; a person requests one on behalf of a Data Product or an Exploration.

Many consumers produce nothing: a Power BI dashboard for a team, an organisation-wide report, an application or an AI agent, an integration that moves data to another system.
The people who read a dashboard (end users) have no place in Portal.
They cannot discover a dashboard, ask to see it, or be granted the data it shows.

An Exploration does not fill that gap.
Its Input Port carries one business justification, and the people added to the Exploration read under it without a justification of their own.

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

### Option 1: Output Ports open to identities

When the owner creates an Output Port, they choose who may consume it: Data Products, identities, or both.
Identities are users and Groups; whether machine users consume as identities or always through a Data Product is an open question.
A dashboard or app is an Output Port of the Data Product that builds it, opened to identities.

* Each identity requests the Output Port itself, with its own business justification, the way a Data Product requests one today.
* The Output Port's Access Type decides the approval, so an Output Port that needs approval or is Invite only works for identities as it does for Data Products ([ADR-0025](./0025-output-port-access-types.md)).
* Access modes give one Output Port different views, mapped to the tool's audiences and row-level security.
* The owner of the readers is the owner of the Data Product.
* With viewer identity the identity holds the grant on the Output Port; with technical identity it gets the reader role on the dashboard.

A stricter variant splits the two kinds of consumer: Data Products only consume Output Ports, and identities only consume a new concept next to them, an audience.
Everything else stays the same.
The split makes every concept explicit, at the cost of a new concept and of publishing twice when Data Products and people need the same data.

### Option 2: Consumption as a separate concept

A Consumption sits next to Data Product and Exploration.
It holds Input Ports on Output Ports of any Data Products, and its Technical Assets are the dashboards and apps.

* Audiences decide who opens which Technical Asset.
* Every new reader who joins an audience gives a business justification, and the Consumption owner approves.
* The Consumption's owner may differ from the owners of the data.
* With viewer identity the readers of a Technical Asset get the grants of the Input Ports it reads.

### Option 3: Dashboard as an Output Port, readers through Explorations

A dashboard or app is an Output Port of the Data Product that builds it.
A reader, or a Group, requests it through an Exploration.

* The business justification is given once, for the Exploration's Input Port; members of the Exploration read under it.
* Access modes map to the tool's audiences and row-level security.
* With viewer identity the Provisioner grants the Exploration's members the data the dashboard reads.

### How the options differ

* **Who requests access.** In Option 1 the identity itself. In Option 2 the reader joins an audience that the Consumption owner manages. In Option 3 the owner of the Exploration, for its members.
* **Who justifies access.** In Options 1 and 2 every reader, or every Group, gives its own justification. In Option 3 only the Exploration does, and its members have none.
* **Different owners without a Data Product.** Only Option 2 lets a team own a dashboard on other teams' data without creating a Data Product for it.

## Comparison per scenario

| Scenario | Option 1: Output Ports open to identities | Option 2: Consumption | Option 3: Readers through Explorations |
|---|---|---|---|
| Team dashboard on own data | An Output Port on the own Data Product, open to identities | A Consumption next to the Data Product; its Input Ports are approved automatically | An Output Port on the own Data Product |
| Organisation-wide dashboard | Readers or Groups request the Output Port; its Access Type decides the approval | Readers join an audience; the Consumption owner approves | One Exploration per reader or Group; the Output Port owner approves |
| Dashboard by another team | That team creates a Data Product for the dashboard | A Consumption owned by that team | Same as Option 1 |
| Combining Data Products | Through the dashboard's own Data Product | Input Ports on several Output Ports | Same as Option 1 |
| Different views | One access mode per view, mapped to the tool's audiences and row-level security | One Technical Asset per view, or viewer identity | Same as Option 1 |
| Viewer identity | Readers hold the grant on the Output Port themselves | Readers get the grants of the Input Ports their Technical Asset reads | The Provisioner grants members the data the dashboard reads |
| Application, agent or integration | An app or API is an Output Port; an integration consumes through a Data Product, or as a machine user if allowed | A Consumption whose Technical Asset reads with a machine user | An app or API is an Output Port; an integration is an Exploration owned by a machine user |
| Business justification | Per request, by a reader or a Group | Per reader who joins an audience | Once per Exploration |
| New concepts | None; an audience in the split variant | Consumption and audience | None |

## Decision Outcome

Open for the team vote.

## Pros and Cons of the Options

### Option 1: Output Ports open to identities

* **Good, because** it adds no concept: datasets, dashboards and APIs are all Output Ports, found and requested in the marketplace.
* **Good, because** every reader justifies their own access, and the Output Port owner sees each reader and why.
* **Good, because** Access Types and access modes work the same for Data Products and identities.
* **Good, because** with viewer identity the reader holds the grant directly, with no grants passed on through another concept.
* **Bad, because** a person now holds an Input Port: an Input Port is held by a Data Product or an identity, which changes the data model and the rules that build on it.
* **Bad, because** an Output Port is no longer only data that others build on, and its owner has to choose who may consume it.
* **Bad, because** a team that only builds a dashboard on other teams' data needs a Data Product.
* **Bad, because** a large audience means many requests, unless Groups request or the Access Type approves automatically.

### Option 2: Consumption as a separate concept

* **Good, because** a team can own a dashboard or app on other teams' data, from several Data Products, without a Data Product of its own.
* **Good, because** the Output Port keeps meaning data that others build on.
* **Bad, because** it is a new concept in the domain, the UI, authorization and the provisioning events.
* **Bad, because** a producer that builds a dashboard on its own data manages a Data Product and a Consumption.
* **Bad, because** it sits close to the Exploration and makes the difference between the two harder to explain.

### Option 3: Dashboard as an Output Port, readers through Explorations

* **Good, because** it adds no concept and uses the request flow that exists.
* **Bad, because** members of an Exploration read without a justification of their own.
* **Bad, because** the name "Exploration" reads as a step towards a Data Product rather than a request for access with a reason, so the concept has to be renamed in the code, the UI, the API and the docs.
* **Bad, because** an Exploration cannot consume an Invite only Output Port, so sensitive dashboards need that rule revisited.
* **Bad, because** with viewer identity the Provisioner grants members the data behind the dashboard, which is not the Output Port they requested.

## Open Questions

1. **Explorations.** With Option 1, people request Output Ports directly. Is an Exploration still needed, only as a personal, time-bound workspace, or not at all?
2. **Machine users.** Does a machine user always consume through a Data Product, because it automates work, or may it consume an Output Port as an identity?
3. **Groups as requester.** Who may request on behalf of a Group, and does its justification cover every member?
4. **The split variant.** Should one Output Port be able to serve both Data Products and identities, or should identities consume a separate audience?
5. **Rules that change.** Which requesters may consume an Invite only Output Port, who receives Announcements, and how the definition of an Output Port covers dashboards.
6. **Moving a Technical Asset.** In Option 2, a dashboard a team built inside its Data Product is rebuilt in a Consumption once others need it. Should Portal move the Technical Asset instead, keeping the underlying resource?
7. **Name.** "Consumption" is a working name for Option 2. See Appendix A for how other tools and open standards name it.

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
