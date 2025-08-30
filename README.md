
# Implementation Overview


## Project Structure Overview

The `src` directory contains the main modules for contract inspection and retrieval:

- **llm/**  
	Components for large language models (LLMs), such as model loading and inference.

- **retriver/**  
	Implements retrieval logic and Weaviate-based indexing/search.
	- `config.py`: Configuration settings for retrieval operations.
	- `retriever.py`: Core retrieval logic for searching and fetching data.
	- **index/**: Indexing utilities.
		- `index_invoker.py`: Invokes document indexing in Weaviate.
		- `util/index_lib.py`: Library functions for PDF partitioning and schema management.
		- `util/content_extractor.py`: Extracts content from partitioned documents.
	- **search/**: Search utilities.
		- `util/search_lib.py`: BM25, vector, and hybrid search logic using Weaviate.

- **query_parser/**  
	Implements query parsing for the RAG system.
	- `utils/parser_lib.py`: Utility functions for query parsing (placeholder for now).
	- `tests/`: Unit tests for query parser components.

These modules work together to enable document indexing, semantic search, query parsing, and retrieval using LLMs and Weaviate.

## Search Functionality (`search.py`)


This module provides search functionalities for collections in a local Weaviate instance. It supports three search types and metadata filtering:


- **BM25 Search**: Uses the BM25 algorithm for keyword-based search.
	- Usage: Set `type="bm25"`
	- Returns results ranked by BM25 relevance.

- **Vector Search**: Uses semantic search via vectorization (requires a vectorizer module in Weaviate).
	- Usage: Set `type="vector"`
	- Returns results based on semantic similarity to the query.

- **Hybrid Search**: Combines keyword and vector search for improved relevance.
	- Usage: Set `type="hybrid"`
	- Returns results using both BM25 and vector similarity.

### Metadata Filtering

All search types support metadata-based filtering. Filters are constructed using the `add_metadata_filters` function, which reads filter configuration (such as date ranges) from `metadata.yml` and applies them to the search query. This allows you to restrict search results based on document metadata (e.g., `effective_date`).

#### Example: Filtering by Effective Date

```python
from src.retriver.weaviate_search.search import weaviate_search, add_metadata_filters
import yaml
from src.retriver.config import METADATA_CONFIG_PATH

metadata_config = yaml.safe_load(open(METADATA_CONFIG_PATH))
results = weaviate_search(
	query="oracle",
	type="hybrid",
	collection="Page",
	limit=5,
	filters=add_metadata_filters(metadata_config["metadata_filter_config"])
)
print("Search Results:", results)
```

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

Create Query parser module to the RAG system to parse the prompt and extract relevant information for retrieval and for the answer generation.

Implement ReRanking for the Retriever module.

