# Initial implementation for searching datasets

## Context and Problem Statement
- ts_rank_cd: a ranking function that takes into account number of occurrences and their positions within the document.
- A, B, C, D assign weights to different fields in our search vector (1.0, 0.4, 0.2, 0.1 respectively).
- websearch_to_tsquery instead of other conversions from input to lexemes to allow users to flexibly filter data.
- core in our search is to allow for multi-word queries

Extra decisions:
- use a penalty for longer documents, can be passed as a parameter to ts_rank_cd
- use fuzzy search capabilities of PostgreSQL to handle typos and approximate matches
- change the weigths assigned to different fields in the search vector

## Decision Drivers


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


### Option 2 – Single-Parent Dataset Model

