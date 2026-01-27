# Improve search

## Context and Problem Statement

We want to improve the search in the application. We want data consumers to be able to find relevant output ports,
using natural language queries.
During a hackathon we have investigated several options. And we want to implement one to improve the search.

Currently we will only focus on providing support for English queries. If by popular demand we want to support other
languages, we can add support for them later.

## Decision Drivers

* Speed (How fast does it offer the results to the users)
* Precision (How accurate are the results)
* Recall (How many relevant results are returned)

## Considered Options

* **Option 1: LLM Search** Pass on results to an LLM and let it rank and return the relevant results.
* **Option 2: Embedding search** Option 2 Use an embedding model to rank and return the relevant results.
* **Option 3: Combined search** Option 3 Use either option 1 or 2, and use a reranker to combine the results with our traditional search and rerank them.

## Decision Outcome

**Chosen option:** *Option 2: Embedding search*. Through our investigation, Option 2 had the best results, and it was fast enough to be used in the application.
The best results were with an opensource small model, ensuring our dependency isn't too big.

### Confirmation

We will switch from the current search to the embedding search.

## Pros and Cons of the Options

### Option 1: LLM Search

* **Good, because** It performs very well.
* **Bad, because** Unclear how to scale this to a large number of output ports and data products.
* **Bad, because** Even with <100 output ports, it's already slow
* **Bad, because** It's not trivial to ensure the LLM returns results in the correct way
* **Bad, because** Need to use a cloud service, which can be expensive, and we probably have to implement multiple integrations

### Option 2: Embedding search

* **Good, because** Small embedding models are fast and good enough for our use case.
* **Good, because** We are able to use open source models, ensure we don't need to implement different models for different clouds/vendors
* **Neutral, because** We have a dependency on pgvector being available on postgres, this is available on Azure and AWS, but might not be on other clouds
* **Bad, because** It increases our image size since we need to include the embedding model
* **Bad, because** It isn't the best performing model
* **Bad, because** It returns all results in a ranked order, and setting a cut-off point isn't trivial

### Option 3: Combined search

* **Good, because** It can combine the best of both worlds
* **Good, because** There are open source models we can use
* **Neutral, because** We haven't investigated how well it performs
* **Bad, because** It increases our image size since we need to include the reranker model
* **Bad, because** Complicated because there are even more knobs to tune

# Investigation results

| Method                           | Speed     | Precision | Recall | Notes                                                                                                                                  |
|----------------------------------|-----------|-----------|--------|----------------------------------------------------------------------------------------------------------------------------------------|
| Current search                   | ~20ms     | 86%       | 48%    | Extremely fast, good precision, very poor coverage (misses many relevant items, especially not adapted for broader business questions) |
| LLM Search with: Claude-3-Haiku  | ~7s       | 91%       | 81%    | Very high precision and coverage, but very slow and inconsistent depending on input/output. Dependency on cloud (AWS Bedrock)          |
| Embedding search: BAAI/bge-large | ~2s *     | 81%       | 91%    | Excellent coverage, good precision, speed not that good.Open source Large model, needs a while to download                             |
| Embedding Bedrock/Cohere v4.0    | ~1.5s *   | 71%       | 77%    | Medium speed, lowest precision among embeddings, okay coverage. Dependency on cloud (AWS Bedrock)                                      |
| Embedding BAAI/bge-small         | ~150ms *  | 76%       | 86%    | Very fast, slightly lower precision and coverage than large, good trade-off for speed-sensitive use. Open source small model           |

* Searches were done without an index, so an index might improve performance. In a first dirty test `BAAI/bge-large` was improved to 700ms, so it's still slower.
