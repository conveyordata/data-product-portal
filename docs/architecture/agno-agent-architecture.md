# Agno Agent Architecture — Architectural Review

> A structured evaluation of design decisions for the Portal × Agno integration.

---

## 1. Current Architecture

### The Core Idea
Each data product in the Portal gets a dedicated Agno agent. That agent is connected to the data product's output ports (postgres tables + an Open Semantic Interchange semantic model). The agent is, in effect, a **domain expert** for that data product: it knows the structure, the meaning, and the access rules of the data it manages.

```
Portal
├── Data Product A
│   ├── Output Port (tables + semantic model)
│   └── Agent A ← expert in A's data
├── Data Product B
│   ├── Output Port (tables + semantic model)
│   └── Agent B ← expert in B's data
└── Data Product C (new, with input ports from A and B)
    ├── Input Port ← A's output
    ├── Input Port ← B's output
    ├── Output Port (tables + semantic model)
    └── Agent C ← expert in C's data + can explore A+B
```

### What the demo proves
1. **Semantic > generic**: an agent with a semantic model layer produces better answers than one with raw SQL access. The semantic model provides intent, not just structure.
2. **Lineage awareness**: when a new data product references input ports, giving its agent access to those ports enables interactive exploration of the source data — accelerating development of the data product itself.

---

## 2. The Internal vs. External Agent Question

### Observation
- **No input ports**: agent exposes only what the data product produces. Useful to *consumers*.
- **With input ports**: agent also has access to source data. Primarily useful to *producers* building the data product.

### Recommendation: split them
| Dimension | External Agent | Internal Agent |
|---|---|---|
| Audience | Data consumers, downstream products | Data product producer / engineer |
| Access | Output ports only | Input ports + output ports |
| Persona | "What can I learn from this data?" | "How do I build this data product?" |
| Lifecycle | Long-lived, published in marketplace | Active during development; may be retired |
| Security boundary | Strict (enforces ToS, no raw SQL) | Relaxed (full dev access) |

**Why this matters**: conflating the two leads to overpowered consumer agents (security risk) or underpowered producer agents (productivity loss). The distinction maps cleanly to the Portal's existing access control model.

**Implementation**: the Portal, when provisioning an agent, can set two roles:
- `external` — read-only on output ports, semantic layer only
- `internal` — read/write on input+output ports, raw SQL allowed

---

## 3. Cross-Product Joins

### Problem
Agent A only knows A's data. Agent B only knows B's data. When Agent C needs a join across A and B, neither A nor B can execute it.

### Option 1: Direct database access for Agent C (current approach)
Give Agent C's internal agent direct connection to A's and B's underlying tables.

- **Pro**: full SQL expressiveness, joins work natively, single query execution
- **Pro**: semantic models of A and B can be merged (see §3a)
- **Con**: Agent C's internal agent must be granted direct DB access to A and B — circumvents agent-based security boundary
- **Con**: tight coupling to A's and B's physical schema

### Option 2: Agent-to-agent routing
Agent C calls Agent A and Agent B separately and combines results in application memory.

- **Pro**: security boundary preserved — C only gets what A and B choose to expose
- **Pro**: A and B can enforce their own ToS per-query
- **Con**: cross-agent joins are expensive and lossy (data serialized, transferred, re-joined in Python)
- **Con**: aggregations across large datasets are impractical

### Option 3: Federated query via DuckDB scratch space
Agents A and B write their query results to a shared DuckDB instance (scoped to the session/user). Agent C then joins within DuckDB.

- **Pro**: enables cross-product joins without direct DB access
- **Pro**: DuckDB is fast and handles in-memory federation well
- **Con**: adds infrastructure complexity (shared ephemeral storage)
- **Con**: still limited by what A and B expose — can't join on unexposed columns
- **Con**: security boundary is the DuckDB instance, not the agent — needs careful scoping

### Option 3a (complement to 1 or 3): Merge semantic models
When a data product has input ports, merge the semantic models of those input ports. Joins can be made explicit based on metadata (e.g., shared dimension keys, foreign-key annotations in OSI).

- **Pro**: agent understands cross-product relationships semantically, not just structurally
- **Pro**: surfaces join paths to LLM — better query generation
- **Pro**: decoupled from physical execution model (works with option 1 or 3)
- **Con**: requires consistent semantic model conventions across data products
- **Con**: join metadata must be maintained (which field in A maps to which field in B)
- **Recommendation**: implement this regardless of which option you choose for execution — it improves query quality

### Verdict
For the **producer/internal agent**: Option 1 (direct access) + Option 3a (merged semantic models). This gives the developer maximum power.
For the **consumer/external agent**: Option 2 with DuckDB scratch space (Option 3) as a performance optimization when large result sets are needed.

---

## 4. User Flow Analysis

### Flow 1: Create a New Data Product

```
User → Intake Agent
             │
             ├─ gather requirements
             ├─ check if an existing data product already satisfies the need (ontology search)
             │       ├─ [match found] → inform user, suggest using existing product, stop
             │       └─ [no match] → continue
             ├─ create new data product
             ├─ discover relevant input data products
             ├─ request access to relevant output ports
             ├─ evaluate terms of service → auto-approve or request human approval
             │       ├─ [human needed] → notify user, provide link to pending requests, stop
             │       └─ [auto-approved] → continue
             └─ hand off to new data product's internal agent
```

#### Question: Discovery via agents or ontology?

**Agent-based discovery** (ask each agent "can you help build X?"):
- **Pro**: agents can reason about their data semantically, handle nuance
- **Pro**: no separate system to maintain
- **Con**: the intake agent must have access to all agents — this means it can *query all data*, regardless of whether the user has access
- **Con**: slow (N round-trips to N agents), expensive, non-deterministic

**Ontology-based discovery** (structured index of data products and their capabilities):
- **Pro**: fast, deterministic, O(1) lookup
- **Pro**: no data exposure during discovery — only metadata is queried
- **Pro**: natural place to encode relationships, domains, and tags
- **Pro**: the Portal already has a marketplace — this is essentially a machine-readable version of it
- **Con**: requires upfront investment in metadata quality
- **Con**: can't reason about implicit semantic connections (e.g., "this table has the data you need but isn't tagged for your use case")

**Recommendation: ontology-first with agent-based refinement**
1. Use an ontology/index (powered by the Portal's existing data product metadata + embeddings/vector search) to narrow candidates.
2. For shortlisted candidates only, query their agents to confirm relevance and check ToS compatibility.
3. This limits agent exposure to a small set, contains the security risk, and keeps latency manageable.

The Portal's existing pgvector integration makes this natural — index data product descriptions, output port schemas, and tags; do semantic search.

#### Security problem: Intake agent knows too much

If the intake agent can call any data product agent, it can extract data the user doesn't have access to.

**Mitigations**:

1. **Agno Workflow isolation**: model discovery as a workflow step where the intake agent only receives metadata responses (description, purpose, ToS summary), not actual data. The agents are instructed to respond to discovery queries with metadata only, not data. Data access only becomes available *after* access is granted and a new agent is provisioned.

2. **Two-phase agent architecture**:
   - Phase 1 (discovery): intake agent calls a `discovery_tool` that queries the ontology/index. No agent-to-agent calls.
   - Phase 2 (access): once access is approved in the Portal, the new data product's internal agent is given its credentials. The intake agent never holds these credentials.

3. **Agent-level ToS enforcement**: each data product agent checks the caller's identity and approved access level before responding to any query. Even if the intake agent asks, the data product agent refuses data queries from non-approved callers.

Option 3 is the most robust and the right long-term answer — it treats each agent as a first-class security principal.

#### Should this be modelled as a workflow?
**Yes**. The flow has clear stages, branching (access approved vs. pending), and human-in-the-loop steps. Agno workflows provide:
- State persistence across async steps (access approval can take days)
- Auditability (what did the intake agent ask, what was returned)
- Deterministic branching (auto-approve vs. human review)
- Resumability after human approval

---

### Flow 2: Ad-hoc Question

```
User → Adhoc Agent
             │
             ├─ identify relevant data products (ontology + agent confirmation)
             ├─ evaluate ToS → auto-approve or request human approval
             │       ├─ [human needed] → notify user, provide link, stop
             │       └─ [auto-approved] → continue
             ├─ provision lightweight data product + agent
             ├─ answer question via lightweight agent
             └─ schedule cleanup (retain audit log)
```

#### Do you need a lightweight data product?

**With a full lightweight data product:**
- Pro: full audit trail (Portal records what was created, accessed, and when)
- Pro: access control is explicit and revocable
- Pro: reproducible (user can re-run the same question later)
- Pro: consistent with how other data products work — no special-casing
- Con: provisioning overhead (even if fast, it's not instant)

**Without (callable factories only):**
- Pro: instant — no Portal round-trip, agent bootstrapped in memory
- Con: no audit trail (security and compliance risk)
- Con: access revocation is harder — where is the grant recorded?
- Con: ToS acceptance is implicit — harder to prove in an audit

**Recommendation: use a lightweight data product**. The audit trail and explicit access grant are not optional in a governed data platform. The overhead can be mitigated by making lightweight provisioning fast (e.g., a `type: ephemeral` data product that skips infrastructure provisioning and only creates the access record and agent config).

#### Can callable factories replace the agent at runtime?
Yes — and you should use them for the *connection bootstrapping* within the lightweight agent, not to replace the agent entirely. Pattern:

```python
def make_agent(data_product_id: str, approved_ports: list[str]) -> Agent:
    db_conn = portal.get_connection(data_product_id, approved_ports)
    semantic_model = portal.get_merged_semantic_model(approved_ports)
    return Agent(tools=[SQLTool(db_conn), SemanticTool(semantic_model)])
```

This gives you runtime flexibility without losing the audit trail (the data product record in the Portal captures `data_product_id` and `approved_ports`).

---

## 5. The Big Question: Do You Need Sub-agents?

### Single agent with tools (alternative)
One powerful agent. It has all the DB connections, all the semantic models, all the Portal MCP tools. It routes internally using tool calls.

**Pros**:
- Simpler operationally (one agent to deploy, monitor, debug)
- Cross-product joins work natively (all connections in scope)
- No agent-to-agent latency

**Cons**:
- Security boundary is the *agent itself*, not a per-data-product principal — a compromised or misused prompt leaks everything
- Context window becomes enormous (all semantic models loaded)
- No natural encapsulation of ToS per data product
- Hard to scale independently per data product
- The "domain expertise" is diluted — a single agent reasoning about 50 data products is worse than 50 specialized agents

### Agent-per-data-product (proposed)
Each agent is a first-class security principal, a domain expert, and a ToS enforcer.

**Pros**:
- Security boundary is clean and enforceable at the agent level
- Semantic models are scoped — smaller context, better reasoning
- Scales independently per data product
- ToS is enforced inside the agent (not just at the Portal layer)
- Treats agents as autonomous entities — mirrors how humans own and govern data products
- Natural mental model: "ask the Orders agent about orders"

**Cons**:
- More complex orchestration (which agent to call? how to combine results?)
- Cross-product joins require federated query strategy (see §3)
- More infrastructure to provision and monitor

### Verdict
The agent-per-data-product model is the right architecture **because**:

1. **Security**: it's the only model where data access can be enforced at query time by a principal that knows its own data.
2. **Domain expertise**: an LLM with a focused, well-scoped semantic model produces better answers than one with a sprawling, generic context.
3. **Autonomy**: it mirrors the data product philosophy — each data product is a product with an owner, a purpose, and a contract. The agent is the conversational interface to that contract.
4. **Governance**: audit logs per agent = audit logs per data product = natural alignment with existing data governance structures.

Sub-agents have real value here. The complexity they introduce is the cost of proper data governance, not unnecessary overhead.

---

## 6. Summary of Recommendations

| Decision | Recommendation |
|---|---|
| Internal vs external agents | Split them. Internal = producer, input+output ports. External = consumer, output ports only. |
| Cross-product joins (producer) | Direct DB access + merged semantic models |
| Cross-product joins (consumer) | Agent-to-agent + DuckDB scratch space for large result sets |
| Discovery mechanism | Ontology-first (Portal metadata + vector search), agent confirmation for shortlist only |
| Intake agent security | Two-phase: discovery returns metadata only; data access only after Portal grant |
| Workflow modelling | Yes — both flows benefit from Agno workflows (state, branching, human-in-the-loop) |
| Lightweight data product | Yes — for audit trail and explicit access record. Make provisioning fast with `ephemeral` type. |
| Callable factories | Use for connection bootstrapping inside agents, not to replace agents |
| Single agent vs sub-agents | Sub-agents. The security, expertise, and governance benefits outweigh the complexity. |

---

## 7. Open Questions / Next Steps

- [ ] Define the `discovery` response schema that data product agents return (metadata-only, no data)
- [ ] Design the `ephemeral` data product type in the Portal (fast provisioning, TTL, auto-cleanup)
- [ ] Define OSI semantic model merge strategy — what metadata is needed to express cross-product joins?
- [ ] Prototype Agno workflow for the "create data product" flow with human-in-the-loop access approval
- [ ] Define agent identity/credentials — how does a data product agent authenticate callers?
- [ ] Evaluate DuckDB scratch space: per-session? per-user? per-workflow-run?
