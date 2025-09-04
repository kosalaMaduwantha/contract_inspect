
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
	- `utils/parser_lib.py`: Utility functions for query parsing.
		- `extract_entities(prompt: str) -> list[str]`:
			- Purpose: Parse a user query and extract named entities (terms, parties, dates, clause names, etc.) that can be used to build retrieval filters and improve document relevance for RAG.
			- Implementation: Calls the Ollama chat API (model `llama3.2`) with a system prompt taken from `src.retriver.config.OLLAMA_SYSTEM_MESSAGES['entity_resolution']` and the user `prompt`. The current implementation returns the model's message content; callers should validate/parse that content into a list of entity strings if needed.
			- Inputs: `prompt` — the user query string.
			- Outputs: Annotated as `list[str]` (expected list of entity strings). Note: the function presently returns the raw LLM response (`response['message']['content']`) so the actual runtime type may be `str` unless the system prompt instructs the model to return a JSON array.
			- Dependencies: `ollama` Python client and a configured `OLLAMA_SYSTEM_MESSAGES` dictionary containing an `entity_resolution` entry.
			- Example usage:

			```python
			from src.query_parser.utils.parser_lib import extract_entities
			entities = extract_entities("Find obligations for Oracle and the vendor related to data retention")
			# entities is expected to be a list of strings (or raw model content that should be parsed)
			```

			- Error modes / edge cases:
				- network or LLM errors when calling Ollama; callers should handle exceptions from the `ollama.chat` call.
				- empty or ambiguous prompts may return an empty list or unexpected text.
				- model responses may be free-form text; to guarantee machine-parseable output, update the system prompt to require a JSON array (recommended).
			- Next steps (recommended): enforce structured output (JSON array) from the system prompt or parse the returned content in `extract_entities` before returning to callers so the function reliably returns `list[str]`.
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

Python version 3.12