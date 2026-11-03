# Consumption of Data by Dashboards, Applications and End Users

**Status:** Proposed. Up for a team vote between Option 1 and Option 2.

## Context and Problem Statement

Portal models two things that hold an Input Port on an Output Port: a Data Product and an Exploration ([ADR-0016](./0016-light-weight-data-products.md)).
Both are kinds of the same base model, and the Input Port references that base model ([ADR-0021](./0021-input-ports-and-input-port-requests.md)).
A person never holds an Input Port; a person only requests one on behalf of a Data Product or an Exploration.
This requester rule is not written down anywhere.
It protects three things, and this ADR states it as three principles:

1. Purposeful: every Input Port has a holder with a stated purpose.
2. Ownership: someone who answers for it.
3. Identity: an identity the Provisioner can grant to.

"Never a person" follows from those three principles.
Explorations already show that a person may consume when wrapped in a container with a purpose and a lifecycle.
Other tools let persons request access directly (Purview, Collibra, Unity Catalog, Witboost); Portal keeps the rule.

Many consumers produce nothing: a Power BI dashboard for a team, an organisation-wide report, an application or an AI agent, an integration that moves data to another system.
Today such a consumer must be modelled as a Data Product, which brings Output Ports, data contracts and a team it does not need, or as an Exploration, which has a single user as owner, cannot be shared and is short-lived.
The people who read a dashboard (end users) have no place in Portal at all.
They cannot discover a dashboard, ask to see it, or be granted the data it shows.

How a dashboard reads its data decides who needs access:

* **Technical identity**: the dashboard reads with its own technical identity, such as a service principal. Only that identity needs a grant on the Output Port, and every reader sees what the dashboard shows.
* **Viewer identity**: the dashboard reads with the identity of each person viewing it (e.g. Power BI single sign-on to Databricks). Every end user needs a grant on the Output Port, and the data platform's row filters and column masks apply per person.

The question is how Portal models a consumer that only consumes, the identities that read through it and their access.

### Terms used in this ADR

* **Consumption**: working name for a consumer that only consumes, such as a dashboard, an application, an agent, a notebook or an integration. See the open question on its name.
* **End user**: one person who reads a Consumption without being on a team that owns data.
* **Audience**: a set of identities (users, Groups and machine users, see [ADR-0023](./0023-external-identities-group-based-auth.md)) that read through a Consumption, linked to the Consumption's Technical Assets they open. A Consumption can have several audiences, for example one that opens a dashboard with personal data and one that opens a dashboard without.

### Scenarios

| Scenario | Description |
|---|---|
| Team dashboard | About 5 readers who know each other. |
| Organisation-wide dashboard | About 500 readers who don't know each other and come and go. |
| Application, agent or integration | An application, an agent, or an integration that moves data to another system inside or outside the organisation, reading with a service principal. |
| Exploration | A time-boxed exploration that may grow into a dashboard later on. |
| Dashboard on own data | The team that owns a Data Product builds a dashboard on its own Output Port. |
| Application deployed by a Data Product | The team that owns a Data Product builds and deploys a web app on its own data, used by end users outside the team. |

## Decision Drivers

1. Both technical identity and viewer identity are supported.
2. The three principles of the requester rule hold.
3. End users discover a dashboard in Portal and request access without joining a team.
4. The Output Port owner sees who reads and why, with lineage to the dashboard, and can revoke access.
5. It scales to large audiences that change often.
6. It is clear for people and the Provisioner what each concept may do, at the lowest extra weight.
7. It fits Groups as owner, audience member and approver.
8. Every consumer that works with data can be listed in Portal, so the organisation sees who uses which Output Port. How much Portal governs beyond listing is the organisation's choice.
9. A team that already owns the data adds a dashboard without extra ceremony; requests and approvals appear only when an ownership boundary is crossed.
10. A team consumes other teams' data, from one or several Data Products, without having a Data Product of its own.

## Out of scope

* Mapping Power BI objects (workspace, semantic model, report, app) onto Portal concepts. This belongs to a later ADR on tools and assets.
* Deciding whether an Output Port is single-technology. That gets its own ADR; a dashboard is never an Output Port, whatever that decision.
* How an Exploration is promoted to a Consumption or a Data Product. The principles are below; the mechanics are a separate effort.
* Column masks and row filters inside the data platform. The data platform enforces them on group membership; Portal only manages who is in which audience.
* Sharing with external parties or the public: provisioning identities for external parties (such as Delta Sharing recipients or partner accounts), approving sharing outside the organisation, and public data without an identity. That needs a separate ADR. External readers of a dashboard already fit as audience members when the identity provider has them as guest users.

## Considered Options

* **Option 1: Consumption as a separate concept**: a Consumption sits next to Data Product and Exploration. It is owned by a user or Group, holds Input Ports and has audiences. It never has Output Ports.
* **Option 2: Consumer-aligned kind of Data Product**: a Data Product type maps to a fixed kind, "consumer-aligned", that may have audiences and may not have Output Ports, the way an Access Type maps to an Access Function ([ADR-0025](./0025-output-port-access-types.md)). Changing the kind to producing upgrades it in place.
* **Option 3: Output Port with audiences**: the producing Data Product adds a dashboard as an Output Port with audiences. It is always owned by the producer.
* **Option 4: Audiences on every Data Product**: no new concept or kind; any Data Product can have audiences.

## Decision Outcome

**Chosen option:** *Option 1: Consumption as a separate concept*, with *Option 2: Consumer-aligned kind of Data Product* as the alternative for the team vote.
Both handle every scenario the same way; they differ in naming, positioning and the upgrade path (see the comparison below).

Publishing data that others build on makes a consumer a Data Product: a Power BI semantic model that other teams reuse belongs in a Data Product.
A Consumption that later needs to publish means creating a Data Product; that is the main cost of Option 1.
A Consumption has a kind (dashboard, application, agent, notebook, integration); the technology lives on its Technical Assets, of types that cannot be shared.
Machine users are technically allowed as owner but discouraged.
It is built as a new kind of the base model that Data Product and Exploration share, which gives it Input Ports, time-bound access and events.
Portal is the source of truth for a Consumption's Input Ports and audiences, and provisions its Technical Assets where a Provisioner supports them.
A dashboard that already exists can be registered as a Consumption; Portal then governs only its data connections and audiences.

### How each scenario works

* **Team or organisation-wide dashboard.** Finance creates a Consumption "Sales attribution", states its purpose and requests the Sales Output Port. The Sales owner approves once. End users ask to join an audience, and the Consumption owner approves.
* **Dashboard on own data.** A dashboard that only the team owning the data reads, such as a quality dashboard, is a Technical Asset of a type that cannot be shared, inside its Data Product. It reads with the Data Product's identity, needs no request and no audience, and is listed as an asset of the Data Product. This works today. It becomes a Consumption once end users outside the team need to see it. This assumes the Provisioner lets a Data Product's team members read the Data Product's own data.
* **Application deployed by a Data Product.** A web app that a Data Product's team builds and deploys keeps living in that Data Product. Once end users outside the team need it, the team creates a Consumption and registers the app as its Technical Asset. The Consumption connects to the Data Product only through Input Ports on its Output Ports, which are approved automatically (see "Same owner").
* **Application, agent or integration.** A Consumption whose Technical Asset reads with its own technical identity, or with each viewer when an app or agent reads on their behalf. An integration that moves data to an operational system or an external party is a Consumption; if other teams build on the target through Portal, it publishes data and is a Data Product.

Any Consumption can also be only listed: it has no audiences, and its Technical Asset reads with its own technical identity. Portal has the lineage, and the organisation decides whether it governs more.

### Combining data

A Consumption holds Input Ports on any number of Output Ports from any Data Products.
It transforms only in its own tool and at query time: measures, relationships, joins across Output Ports, app logic, prompts.
The line is the kind of combining, not the number of sources:

| Combining | Example | Where it belongs |
|---|---|---|
| Light: relate a fact to a dimension, put sources side by side | Sales by region, with the region dimension from a reference Data Product | Consumption |
| Heavy: new logic and meaning, persisted and scheduled | Sales attribution from sales and HR data with commission rules | Data Product: it needs a schema and a job |

When several Consumptions repeat the same join or logic, it should move upstream into a Data Product.

### Audiences

* An audience is linked to the Technical Assets its members open. One audience can open several Technical Assets, so joining it once gives access to all of them.
* An audience belongs to one Consumption and is deleted with it. Reuse comes from putting the same Group from the identity provider in several audiences; Portal keeps Groups flat ([ADR-0023](./0023-external-identities-group-based-auth.md)), so an audience is not a Group of Groups.
* Members are users, Groups and machine users.
* The Consumption's owners create audiences, add members and approve requests to join.
* The Output Port owner approves the Consumption's Input Port once, following the Output Port's Access Function as today. There is no cap on an audience and no approval per member by the Output Port owner; their control is revoking the Input Port.
* Membership of a Group follows the identity provider. A change to a Group triggers a reconcile of the Consumptions it sits in.
* Through lineage the Output Port owner sees the Consumption, its purpose, and its audiences with their Groups, machine users and individual end users. Members of a Group are not expanded.
* Membership is permanent until removed.
* Removing an Input Port or a Technical Asset removes its links. An audience left without links stays, and its members lose the access until it is linked to a Technical Asset again.

Sensitive data is split with Output Ports and Technical Assets.
Different data or different dashboards for different readers means different Technical Assets.
For example, the Sales Data Product publishes "Customers" and "Customers PII", and the Revenue Consumption holds an Input Port on each.
Its dashboard "Revenue" reads "Customers" and is opened by audience "Sales"; its dashboard "Revenue with PII" reads both and is opened by audience "Compliance".
Only Compliance sees the personal data. With viewer identity, Sales members don't even hold the grant on "Customers PII".

```mermaid
flowchart LR
    subgraph Producer[Data Product: Sales]
        OP1[Output Port: Customers]
        OP2[Output Port: Customers PII]
    end
    subgraph Consumption[Consumption: Revenue]
        IP1[Input Port]
        IP2[Input Port]
        TA1[Technical Asset: Revenue]
        TA2[Technical Asset: Revenue with PII]
        A1[Audience: Sales]
        A2[Audience: Compliance]
    end
    OP1 -->|approved once| IP1
    OP2 -->|approved once| IP2
    IP1 --> TA1
    IP1 --> TA2
    IP2 --> TA2
    A1 -.->|opens| TA1
    A2 -.->|opens| TA2
    A1 ---|asks to join, Consumption owner approves| EU[End user]
    A2 ---|added by Consumption owner| G[Group]
```

### Roles and data grants

A Consumption has access to all the data of its Input Ports, the way a Data Product does.
Its Technical Assets use that data as they like; the Consumption's team decides what a dashboard shows.
An audience only decides who opens which Technical Asset: the Consumption's owner is admin of its Technical Assets, its team members are contributors, and the members of the audiences linked to an asset are its readers.

Each Technical Asset reads with technical identity or viewer identity (see "Context and Problem Statement"), set on the asset:

* **Technical identity**: the asset's identity gets the grants of the Consumption's Input Ports.
* **Viewer identity**: the asset declares which Input Ports it reads, and its readers get only those grants.

Appendix C works out what each reader sees for one dashboard.
A Technical Asset's identity may not write the data into storage that others read, because that would be publishing without a Data Product.
Which roles each type of Technical Asset offers, and how they map onto a tool, belongs to the later ADR on tools and assets.

### How a person reads data

A person reads data in only three ways:

1. Through an Exploration, for themselves.
2. As a team member of the Data Product that owns the data.
3. As an audience member of a Consumption.

Every direct access that a person or Group has today moves to one of these three: an app or dashboard with direct assignments becomes a Consumption with those people and Groups as its audience, and an Exploration is the safe temporary landing until the access finds its purpose.
There is no catch-all Consumption for access without a purpose.

An Exploration is a personal, short-lived starting point that can grow, one way and by its owner, into a Consumption or a Data Product.
Promotion never extends access silently: the Output Port owner approves the Input Ports again. How promotion works is out of scope; Appendix D compares the three.

### Same owner

When the requester already holds approve rights on the Output Port, the request is approved automatically and recorded.
This is the permission the existing "grant directly" endpoint checks.
It applies to Data Products too: today a Data Product requesting its own team's Output Port goes to pending and the team approves itself.

### Confirmation

* A Consumption is a new kind of the shared base model, owned by a user or Group, that holds Input Ports and has audiences, and never has Output Ports.
* Persons never hold an Input Port; every identity that reads through a Consumption is an audience member or the technical identity of one of its Technical Assets.
* Audiences are linked to Technical Assets. Their members get the reader role on those Technical Assets.
* Each Technical Asset reads with its own technical identity, which gets the grants of the Consumption's Input Ports, or with each viewer's. With viewer identity it declares which Input Ports it reads, and its readers get only those grants.
* Lineage shows the Output Port owner the Consumptions that read its Output Ports and their audiences.
* Requests from someone who holds approve rights on the Output Port are approved automatically, for Consumptions and Data Products.
* A dashboard that only the owning team reads stays a not-shareable Technical Asset in its Data Product.
* Explorations stay as they are, as a lifecycle stage.

## Pros and Cons of the Options

### Comparison

🟢 good, 🟡 works with friction, 🔴 fails.

| | Option 1: Separate concept | Option 2: Consumer-aligned kind | Option 3: Output Port with audiences | Option 4: Audiences on every Data Product |
|---|---|---|---|---|
| Consume other teams' data without a Data Product, from several Data Products | 🟢 | 🟡 needs a Data Product, a lighter kind | 🔴 only the producer's own data | 🔴 needs a Data Product |
| Clear for people and the Provisioner | 🟢 | 🟢 the Provisioner reads the kind | 🟡 | 🔴 every Data Product can do everything |
| Upgrade to publishing | 🔴 create a Data Product | 🟢 change the kind in place | n/a | 🟢 nothing to change |
| Roles and Groups | 🟡 a new role scope | 🟢 reuses Data Product roles | 🟢 | 🟢 |
| Catalog growth | 🟢 a separate list | 🟡 many Data Products, needs a filter by kind | 🟢 | 🔴 producing and consuming mixed |
| "A dashboard on its own is not a Data Product" | 🟢 | 🟡 a dashboard is called a Data Product | 🟡 an Output Port nobody builds on | 🔴 |
| New concept | 🔴 yes | 🟡 types gain behaviour | 🟢 none | 🟢 none |

### Option 1: Consumption as a separate concept

* **Good, because** it is the clearest: what a Consumption can and cannot do is visible in the concept, for people and for the Provisioner.
* **Good, because** a team consumes other teams' data, from several Data Products, without a Data Product of its own.
* **Good, because** the infrastructure is light: no schema for shared data, no pipelines, no Output Ports. Its profile is close to an Exploration's.
* **Good, because** the catalog keeps Data Products for data that others build on.
* **Bad, because** it is a new concept in the domain, the UI, authorization and the provisioning events.
* **Bad, because** a Consumption that needs to publish later means creating a Data Product.
* **Bad, because** lineage stops where an integration or working storage copies the data.

### Option 2: Consumer-aligned kind of Data Product

* **Good, because** a consumer-aligned Data Product upgrades to producing in place: owner, Input Ports and audiences stay.
* **Good, because** it reuses Data Product roles, Groups, UI and events.
* **Good, because** the fixed kind keeps it as clear for the Provisioner as Option 1.
* **Neutral, because** "consumer-aligned Data Product" is an established data mesh term.
* **Bad, because** Data Product types are labels without behaviour today; giving them behaviour is new.
* **Bad, because** every dashboard becomes a Data Product, so the catalog grows and needs a filter by kind.
* **Bad, because** a dashboard is then called a Data Product, while a dashboard on its own publishes no data for others to build on.

### Option 3: Output Port with audiences

* **Good, because** it needs no new concept and reuses the marketplace.
* **Bad, because** only the producer can build it, so another team can't build on someone else's data, and combining several Data Products is impossible.
* **Bad, because** it dilutes an Output Port: it is no longer something other Data Products build on.

### Option 4: Audiences on every Data Product

* **Good, because** it needs no new concept and nothing changes when a Data Product starts publishing.
* **Bad, because** every Data Product can do everything, so the Provisioner handles every combination.
* **Bad, because** a producing Data Product would let end users read the data behind its Input Ports.
* **Bad, because** every dashboard needs a Data Product.

### Audiences

* **Good, because** it is simple for people and builders: the Consumption reads the data like a Data Product, and an audience only decides who opens which Technical Asset.
* **Good, because** with viewer identity a person holds only the grants of the asset they open, not everything the Consumption reads.
* **Good, because** personal data reaches only the audiences that open a Technical Asset reading it, by reusing Output Ports and their Access Functions.
* **Bad, because** different data for different readers always needs a separate Technical Asset, also with viewer identity.
* **Good, because** one mechanism covers viewers, service principals and integrations.
* **Bad, because** after approving the Input Port, the Output Port owner fully trusts the Consumption owner with who reads the data; their control is revoking the Input Port.
* **Bad, because** new members of a Group in the identity provider get access without anyone in Portal approving them.

## Open Questions

1. **Name.** "Consumption" is a working name for Option 1; Option 2 would use "consumer-aligned Data Product". Candidates for Option 1:
   * Consumption: neutral, used by no tool or standard.
   * Exposure: dbt's term, but it runs opposite to Data Products exposing data through Output Ports.
   * Data Usage: used in Open Data Mesh's DPDS, Bitol's ODPS and Collibra, and carries the purpose.
   * Use Case: used in the Open Data Product Specification and Purview, and carries the purpose, but it is generic.
   * Data App: concrete for business users, but a notebook is not an app.

   Rejected: Consumer (to avoid per `CONTEXT.md`), Sink (jargon that suggests writing), Terminal, Endpoint and Destination (clash with existing meanings), Subscriber and Recipient (they name a party, not a thing).
   See Appendix A for how other tools and open standards name it.
2. **Machine users as owner.** Should Portal block machine users as owner of a Consumption or a Data Product, or only discourage it?
3. **Lifecycle.** Deletion, Finalizers and provisioning events for a Consumption, how an event identifies it and its audiences (the `requester` of [ADR-0019](./0019-event-payload-scoping.md)), and the reconcile when a Group in an audience changes.
4. **Discoverability.** The marketplace lists Output Ports for teams that build on data. End users need to find Consumptions instead:
   * Do Consumptions appear in the marketplace next to Output Ports, in a section of their own, or only through the BI tool sending end users to Portal?
   * An end user on an Output Port page cannot request it; the page points to the Consumptions built on it.
   * A Consumption has a Visibility like a Data Product ([ADR-0022](./0022-data-product-visibility.md)), so a personal dashboard stays out of search. This is the leaning.
   * The cart is for Input Port requests; joining an audience is a different flow.
5. **Organisation policy.** Whether a dashboard is only listed or also governed is decided per Consumption by its owner. Should an organisation be able to require listing or governance through Portal, for example for every dashboard that uses viewer identity?

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

## Appendix B: Ideas from other tools

Not part of this decision.
These come from the tools in Appendix A and could be added to a Consumption later:

* Purpose and attestations on a request (Purview, Collibra).
* Expiry and access reviews (Entra, Collibra).
* Manager approval as an extra tier (Purview).
* Portal as the access front door, through the request redirect of Unity Catalog and the access message of Power BI apps.
* Usage statistics on a dashboard (DataHub), and flagging Consumptions that repeat the same combination of Output Ports as a candidate for a Data Product.

## Appendix C: Example: personal data for some readers

The Revenue Consumption from "Audiences" has a dashboard "Revenue" that reads "Customers", opened by audience "Sales", and a dashboard "Revenue with PII" that reads "Customers" and "Customers PII", opened by audience "Compliance".
The Sales Data Product also has a row filter in the data platform on both Output Ports: a person sees only the customers of their own region.

Two levels decide what a person sees:

1. **Which Output Ports**: the Technical Asset their audience opens, managed by the Consumption owner in Portal.
2. **Which rows and columns**: row filters and column masks on the Output Port, managed by the Output Port owner in the data platform (out of scope of this ADR).

| Option | A Sales member in region North sees | A Compliance member in region South sees | Why |
|---|---|---|---|
| Viewer identity | Customers of North, without personal data | Customers of South, with personal data | Each person queries with their own grants, so both levels apply per person. |
| Technical identity | All regions, without personal data | All regions, with personal data | Each dashboard's technical identity reads both Output Ports and is not filtered by region. The split holds only because "Revenue" doesn't show personal data; the row filter does not apply. |
| Technical identity, with the BI tool's row-level security | What the dashboard's own rules allow | What the dashboard's own rules allow | The Consumption owner rebuilds the row filter in the BI tool. The data platform's filter no longer protects the data. |

Use viewer identity when readers must see different data.
Technical identity fits when every reader may see everything the Consumption reads, such as an application with one purpose or an integration.

## Appendix D: Exploration, Consumption and Data Product

| | Exploration | Consumption | Data Product |
|---|---|---|---|
| Lifespan | Short, personal, may be thrown away | Long-lived | Long-lived |
| Owner | One user | User or Group | User or Group |
| Who reads | Only the owner | Its audiences | Its team, and other Data Products through Output Ports |
| Access | Time-bound | Permanent until revoked | Permanent until revoked |
| Shares | Nothing | A dashboard, app or agent with its audiences | Data, through Output Ports |
| Identity | Its owner | Its Technical Assets' own, or each reader's | Its own |
| Roles on its Technical Assets | No | Admin, contributor and reader | No |
| Schema for shared data, pipelines that write tables | No | No | Yes |
| Output Ports, data contracts, data quality | No | No | Yes |
| Private storage nobody else reads | Scratch space where the owner writes tables | Working storage only, as Technical Assets: import cache, app state, vector index, staging folder | Its own schema |
| Runtime or presentation | No | Yes, as Technical Assets: Power BI workspace and app, app hosting, serving endpoint, connection to the target system | No |

The Provisioner SDK gets a new resource type for a Consumption, next to Data Product, Exploration and Domain.
