# ADR 0001: Datasets Belong to a Single Data Product

## Status
Accepted

## Context
Originally, datasets in our system could be composed of data outputs originating from multiple data products.
This design was flexible, but it introduced significant complexity:
- Ownership and lineage tracking became difficult, as datasets could span multiple product boundaries.
- The UX was clunky because every object could be somehow linked, resulting in a lot of clicks everywhere.
- In our current user base we see barely any usage of this feature, which means we introduce complexity and flexibility for little benefit.

As the platform evolves toward stronger product boundaries and clearer ownership, this flexibility is no longer beneficial.

## Decision
We will change the model so that **each dataset belongs to a single data product**.

In this new design:
- Data outputs linked to a dataset must all originate from the same parent data product.
- Cross-product combinations are achieved by requesting access to a dataset from within a data product.
- Datasets will be linked to a data product at creation time.

## Consequences
**Positive:**
- Clearer data lineage and ownership.
- Simplified governance, access control, and auditing.
- Reduced operational complexity and fewer cross-product dependencies.

**Negative:**
- Some existing datasets that combined outputs from multiple products will need to be identified and refactored.

**Migration considerations:**
- Introduce validation to ensure that all outputs in a dataset share the same parent product.
- Provide migration tooling to split or reassign existing multi-product datasets.

## Alternatives Considered
1. **Keep multi-product datasets:** Retain flexibility but continue complexity and unclear ownership.
2. **Single parent model (chosen):** Simplifies ownership and governance. Flexibility is not really used right now.
