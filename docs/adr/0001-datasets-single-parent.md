# Datasets Belong to a Single Data Product

## Context and Problem Statement

Originally, datasets in our system could be composed of data outputs originating from multiple data products.
While this design offered flexibility, it introduced significant complexity and confusion for both users and maintainers.

Ownership and lineage tracking became difficult, as datasets could span multiple product boundaries. The user experience also suffered because almost any object could be linked, creating excessive complexity and unnecessary navigation steps.

In practice, we observed very little usage of multi-product datasets, suggesting that this flexibility adds complexity with minimal real-world benefit.
As the platform evolves toward clearer product ownership and stronger boundaries, this flexibility is no longer justified.

## Decision Drivers

* Simplify ownership and data lineage.
* Improve user experience and reduce unnecessary linking complexity.
* Strengthen product boundaries and governance.
* Align with actual usage patterns (low use of cross-product datasets).
* Reduce operational and maintenance overhead.

## Considered Options

* **Option 1:** Keep multi-product datasets.
* **Option 2:** Move to a single-parent (single data product) dataset model.

## Decision Outcome

**Chosen option:** *Option 2 – Move to a single-parent dataset model*, because it simplifies ownership and governance, aligns with product boundaries, and matches real user behavior without sacrificing critical functionality.

### Confirmation

This change will be confirmed by:

* Schema validation ensuring all data outputs within a dataset share the same parent product.
* Migration tooling to identify and reassign existing multi-product datasets.
* Code and model reviews verifying that dataset creation enforces single-product linkage.

## Pros and Cons of the Options

### Option 1 – Keep Multi-Product Datasets

* **Good, because** it preserves flexibility for advanced users.
* **Neutral, because** it maintains the current system behavior.
* **Bad, because** it leads to unclear ownership and complex lineage.
* **Bad, because** it complicates UX, permissions, and governance.
* **Bad, because** it increases maintenance and debugging burden for limited benefit.
* **Bad, because** it currently is not really used.

### Option 2 – Single-Parent Dataset Model

* **Good, because** ownership, governance, and lineage are simplified.
* **Good, because** it matches actual user behavior and reduces cognitive load.
* **Good, because** the data model and UI become easier to maintain.
* **Good, because** certain links are automatically in place, lowering the amount of UX overhead.
* **Bad, because** migration requires effort to update legacy datasets, they need to be identified and refactored.
* **Neutral, because** flexibility is reduced, but the trade-off is intentional and low-impact.
