
# Implementation Overview 


## Project Structure Overview

The project is structured as follows:

- **src/**: Main source code directory.
  - **core/**: Core modules for the RAG system.
    - `config.py`: Configuration settings, including Weaviate schema, Ollama system messages, and paths.
    - `rag.py`: Main RAG pipeline implementation, integrating entity extraction, retrieval, and answer generation.
    - **prompt_processor/**: Handles prompt processing for the RAG system.
      - `prompt_processor.py`: Functions for entity extraction, context construction, and answer generation using LLMs.
    - **retriever/**: Retrieval logic and Weaviate-based indexing/search.
      - `index_invoker.py`: Invokes document indexing in Weaviate.
      - **util/**: Utility functions.
        - `search_lib.py`: BM25, vector, and hybrid search logic using Weaviate.
    - **spi/**: Service Provider Interface for LLMs.
      - `llm_spi.py`: Interface definitions for LLM adapters.
  - **llm/**: Components for large language models (LLMs), such as model loading and inference.
  - **sp_adapters/**: Service provider adapters.
    - `ollama_llm_sp_adapter.py`: Adapter for Ollama LLM integration.

- **appendix/**: Additional utilities.
  - `add_data.py`: Script to add data to the database.
  - `create_collection.py`: Script to create Weaviate collections.
  - `db_connection.py`: Database connection utilities.
  - `query_collection.py`: Script to query collections.

- **exact_match/**: Exact match search implementations.
  - `bm25_indexer.py`: BM25 indexing.
  - `bm25_scoring_search.py`: BM25 scoring and search.

- **pdf-processing/**: PDF processing utilities.
  - `partition_pdf.py`: PDF partitioning logic.

- **semantic_search/**: Semantic search implementations.

- **spacy_named_entity_recognition/**: Named entity recognition using SpaCy.
  - `test.py`: Test script for NER.

- **compose-files/**: Docker Compose files.
  - `compose-weaviate.yml`: Weaviate setup.

- **data/**: Data files.
  - `Oracle_Cloud_Agreement.pdf`: Sample contract document.

- **env/**: Python virtual environment.

- `metadata.yml`: Metadata configuration file.

- `requirements.txt`: Python dependencies.

These modules work together to enable document indexing, semantic search, query parsing, and retrieval using LLMs and Weaviate.

## Search Functionality (`search_lib.py`)


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
from src.core.retriever.util.search_lib import weaviate_search, add_metadata_filters
import yaml
from src.core.config import METADATA_CONFIG_PATH

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

#### Main Function: `weaviate_search(query, type, collection, limit, filters=None) -> list[str]`

- **Parameters**:
	- `query`: The search string.
	- `type`: Search type (`bm25`, `vector`, or `hybrid`).
	- `collection`: The name of the collection to search (e.g., `"Page"`).
	- `limit`: Maximum number of results to return.
	- `filters`: Optional tuple of filters to apply.

- **Returns**: A list of strings containing the content of the retrieved documents.

- **Error Handling**: Prints an error message if the search fails (e.g., missing vectorizer for vector search).

## RAG Pipeline

The RAG (Retrieval-Augmented Generation) system is implemented in `src/core/rag.py`. It integrates the following components:

1. **Entity Extraction**: Uses `prompt_processor.extract_entities` to extract relevant entities from the user query.
2. **Retrieval**: Calls `weaviate_search` with the extracted entities to retrieve relevant document passages.
3. **Context Construction**: Uses `prompt_processor.create_query_context` to build a context from the retrieved passages and the original query.
4. **Answer Generation**: Uses `prompt_processor.generate_answer` to generate a final answer based on the constructed context.

### Example Usage

```python
from src.core.rag import invoke_rag

result = invoke_rag(
    query="What is the Oracle open source agreement?",
    query_type="hybrid",
    collection="Page",
    limit=2
)
print("Answer:", result)
```

This pipeline provides end-to-end question answering over contract documents.

## TODO

- [x] Create Query parser module (implemented as prompt_processor)
- [ ] Implement ReRanking for the Retriever module.

Python version 3.12

The following features are implemented in the RAG pipeline:

- Query Processing: Entity extraction from user queries.
- Document Ranking: Retrieval using BM25, vector, or hybrid search.
- Context Construction: Aggregation of retrieved passages into context.
- Generation Module: Answer generation using LLM.
- Post-processing: Basic output formatting.
- Evaluation & Monitoring: Basic logging in place.

Future enhancements:

- Feedback Loop: Collect user feedback to improve quality.
- Advanced ReRanking: Implement more sophisticated ranking algorithms.