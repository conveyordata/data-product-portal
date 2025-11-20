# Postgres full text search (FTS) for searching output ports

## Context and Problem Statement

We are introducing full-text search for output ports using PostgreSQL’s built-in capabilities.
PostgreSQL FTS is simple to implement, performant enough for our current needs, and provides a good foundation for future improvements.

This ADR documents the configuration decisions made for the initial implementation, covering key choices such as ranking,
field selection, query handling, weighting, indexing, and future extensions.

## Key Decisions to Make

- Which ranking function to use
- Which fields to include in the search vector
- How to transform user queries into lexemes
- Whether to apply different weights per field
- When to trigger reindexing
- How to handle varying document lengths

## Decision drivers

We aim for a balanced trade-off between simplicity and quality.
The initial version should be a strong baseline implementation that can evolve over time.
We recognize that even advanced search configurations won’t satisfy all edge cases.

## Decisions

### Ranking function
Use ts_rank_cd for scoring, as it considers term proximity (cover density).
Alternatives like ts_rank lack this normalization, and a custom ranking function would be overkill at this stage.
I also opted to normalize the score between 0 and 1.

### Fields included
Index only title and description fields of the output port and technical assets.
These contain the most relevant data; excluding product and tag info keeps indexing simpler.

### Query transformation
Use websearch_to_tsquery for flexible multi-word queries at the cost of making query syntaxt more complex for users.
plainto_tsquery is simpler but too restrictive as it does not allow users to specify whether they want OR/AND between their words.

The rules of websearch_to_tsquery are:
- unquoted text: text not inside quote marks will be converted to terms separated by & operators, as if processed by plainto_tsquery.
- "quoted text": text inside quote marks will be converted to terms separated by <-> operators, as if processed by phraseto_tsquery.
- OR: the word “or” will be converted to the | operator.
- -: a dash will be converted to the ! operator.

For the full details look at the [Postgres documentation](https://www.postgresql.org/docs/current/textsearch-controls.html#TEXTSEARCH-PARSING-QUERIES)

### Field weighting

Apply two weights:
- A (=1.0): titles (output port + technical asset)
- B (=0.4): descriptions (output port + technical asset)

### Indexing strategy
Use a GIN index on a specific search column of type tsvector.
Reindex automatically when any indexed field changes.
Periodic reindexing is an alternative but unnecessary for our current dataset size.
I would prefer to have the most up-to-date search experience.

### Fuzzy search
Not included in this version. May be added later to handle typos and near matches.

### Document length handling
No normalization for document length in this version.
Current fields are short, so impact should be minimal. In Future revisions we might revisit this.
