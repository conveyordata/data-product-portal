# Data Product Portal

The portal where teams publish Data Products, expose data through Output Ports, and request access to each other's data.

## Language

### Products and ports

**Data Product**:
A team-owned unit of data work that consumes data through Input Ports and exposes data through Output Ports.

**Output Port**:
A published, consumable dataset owned by one Data Product.
_Avoid_: Dataset

**Input Port**:
A Data Product's approved or pending link to consume another Data Product's Output Port.
_Avoid_: Dataset link

**Consuming Data Product**:
A Data Product that has an approved Input Port on a given Output Port.
_Avoid_: Consumer (when the Data Product is meant, not a user)

### Visibility and access

**Visibility**:
Whether a Data Product is Discoverable (visible to every authenticated user) or Hidden (visible only to its members). Fixed at creation.
_Avoid_: Private Data Product, public Data Product

**Access Function**:
One of three fixed behaviours that governs an Output Port: Auto-approve, Approval required, or Invite only (hidden and approval required).
_Avoid_: private, public

**Access Type**:
An admin-defined label on an Output Port (e.g. "Need to know") that maps to exactly one Access Function. Many Access Types may map to the same Access Function; only the name differs.
_Avoid_: Classification, sensitivity label

## Relationships

- An **Output Port** has exactly one **Access Type**; its **Access Function** is the Access Type's.
- An **Output Port** of a **Hidden** **Data Product** must have an Access Type mapped to **Invite only**.
- At least one **Access Type** is always mapped to **Invite only**.
- Members of a **Consuming Data Product** may read an **Invite only** **Output Port** it consumes; nobody else outside the owning Data Product sees it.
