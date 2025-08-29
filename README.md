
# Implementation Overview

The `src` directory contains the main modules for contract inspection and retrieval:

- **llm/**: Components related to large language models (LLMs), such as model loading, inference, or integration.
- **retriver/**: Implements retrieval logic and Weaviate-based indexing/search.
	- `config.py`: Configuration settings for retrieval operations.
	- `retriever.py`: Core retrieval logic for searching and fetching data.
	- **weaviate_index/**: Utilities for indexing data in Weaviate.
		- `index_invoker.py`: Invokes indexing operations in Weaviate.
		- `index_lib.py`: Library functions for data indexing.
	- **weaviate_search/**: Utilities for searching indexed data in Weaviate.
		- `search.py`: Search logic using Weaviate's API.

These modules work together to enable document indexing, semantic search, and retrieval using LLMs and Weaviate.

# Search Functionality (`search.py`)

This module provides search functionalities for collections in a local Weaviate instance. It supports three search types:

- **BM25 Search**: Uses the BM25 algorithm for keyword-based search.
	- Usage: Set `type="bm25"`
	- Returns results ranked by BM25 relevance.

- **Vector Search**: Uses semantic search via vectorization (requires a vectorizer module in Weaviate).
	- Usage: Set `type="vector"`
	- Returns results based on semantic similarity to the query.

- **Hybrid Search**: Combines keyword and vector search for improved relevance.
	- Usage: Set `type="hybrid"`
	- Returns results using both BM25 and vector similarity.

#### Main Function: `weaviate_search(query, type, collection, limit)`

- **Parameters**:
	- `query`: The search string.
	- `type`: Search type (`bm25`, `vector`, or `hybrid`).
	- `collection`: The name of the collection to search (e.g., `"Page"`).
	- `limit`: Maximum number of results to return.

- **Returns**: Search results from the specified collection.

- **Error Handling**: Prints an error message if the search fails (e.g., missing vectorizer for vector search).

#### Example Usage

```python
results = weaviate_search("oracle", "hybrid", "Page", 5)
print("Search Results:", results)
```

## TODO

- Implement metadata filtering for each search type.

