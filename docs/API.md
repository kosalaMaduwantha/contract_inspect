# API Documentation

This document provides comprehensive API reference for the Contract Inspector system.

## Table of Contents

- [Overview](#overview)
- [Core APIs](#core-apis)
- [Search APIs](#search-apis)
- [Document Processing APIs](#document-processing-apis)
- [Configuration APIs](#configuration-apis)
- [Adapter APIs](#adapter-apis)
- [Error Handling](#error-handling)
- [Examples](#examples)

## Overview

The Contract Inspector system provides several layers of APIs:

1. **High-level RAG API**: Complete query processing pipeline
2. **Search APIs**: Direct search functionality 
3. **Document Processing APIs**: PDF parsing and indexing
4. **Configuration APIs**: System configuration management
5. **Adapter APIs**: Low-level provider interfaces

## Core APIs

### RAG Pipeline API

#### `invoke_rag(query, query_type, collection, limit) -> str`

Main entry point for the RAG (Retrieval-Augmented Generation) pipeline.

**Parameters:**
- `query` (str): Natural language question about contracts
- `query_type` (str): Search strategy - `"bm25"`, `"vector"`, or `"hybrid"`
- `collection` (str): Database collection name (typically `"Page"`)
- `limit` (int): Maximum number of documents to retrieve for context

**Returns:**
- `str`: Generated answer based on retrieved documents

**Raises:**
- `RuntimeError`: If adapters are not initialized
- `ValueError`: If query is empty or invalid
- `VectorDBError`: If database search fails

**Example:**
```python
from src.core.rag import invoke_rag

answer = invoke_rag(
    query="What are the payment terms in the Oracle agreement?",
    query_type="hybrid",
    collection="Page", 
    limit=5
)
print(answer)
```

**Internal Process:**
1. Extract entities from query using LLM
2. Search for relevant documents using specified strategy
3. Construct context from retrieved documents  
4. Generate answer using LLM with context

## Search APIs

### Vector Search API

#### `weaviate_search(query, type, collection, limit, filters=None) -> list[str]`

Direct interface to the vector database search functionality.

**Location:** `src/core/retriver/util/search_lib.py`

**Parameters:**
- `query` (str): Search query text
- `type` (str): Search type - `"bm25"`, `"vector"`, or `"hybrid"`
- `collection` (str): Target collection name
- `limit` (int): Maximum results to return (1-100)
- `filters` (FilterSpec, optional): Metadata filters

**Returns:**
- `list[str]`: List of document content strings

**Search Types:**

##### BM25 Search
Keyword-based search using TF-IDF scoring.
```python
results = weaviate_search("payment terms", "bm25", "Page", 10)
```

##### Vector Search  
Semantic search using embeddings.
```python
results = weaviate_search("contract obligations", "vector", "Page", 5)
```

##### Hybrid Search
Combines BM25 and vector search for optimal relevance.
```python
results = weaviate_search("termination clause", "hybrid", "Page", 3)
```

#### `add_metadata_filters(filter_config) -> FilterSpec`

Creates metadata filters from configuration.

**Parameters:**
- `filter_config` (dict): Filter configuration from metadata.yml

**Returns:**
- `FilterSpec`: Filter object for search queries

**Example:**
```python
from src.core.retriver.util.search_lib import add_metadata_filters
import yaml

config = yaml.safe_load(open("metadata.yml"))
filters = add_metadata_filters(config["metadata_filter_config"])

results = weaviate_search(
    query="oracle cloud",
    type="hybrid", 
    collection="Page",
    limit=5,
    filters=filters
)
```

### Search Utility Functions

#### `init(adapter) -> None`

Initialize the search library with a vector database adapter.

**Parameters:**
- `adapter` (VectorDBSPI): Vector database adapter instance

#### `clear_vector_db_adapter() -> None`

Clear the module-level adapter (useful for testing).

## Document Processing APIs

### PDF Processing API

#### `partition_pdf(filename, **kwargs) -> list`

Partition PDF documents into structured elements.

**Location:** `src/core/retriver/util/index_lib.py`

**Parameters:**
- `filename` (str | Path): Path to PDF file
- `infer_table_structure` (bool, optional): Extract table structure
- `include_page_breaks` (bool, optional): Include page break markers  
- `unique_element_ids` (bool, optional): Generate unique element IDs

**Returns:**
- `list`: Partitioned document elements

**Example:**
```python
from src.core.retriver.util.index_lib import partition_pdf
from pathlib import Path

elements = partition_pdf(
    filename=Path("data/contract.pdf"),
    infer_table_structure=True,
    include_page_breaks=False,
    unique_element_ids=True
)
```

### Content Extraction API

#### `ContentExtractor` Class

Processes partitioned elements and extracts structured content.

**Constructor:**
```python
ContentExtractor(document_path: Path, metadata: dict)
```

**Methods:**

##### `consume_elements(elements) -> None`
Process a list of document elements.

**Parameters:**
- `elements` (list): Output from `partition_pdf()`

##### `get_processed_content() -> list[dict]`
Get extracted content as structured data.

**Returns:**
- `list[dict]`: List of page objects with metadata

**Example:**
```python
from src.core.retriver.util.index_lib import ContentExtractor
from pathlib import Path

metadata = {
    "effective_date": datetime(2025, 1, 1),
    "provider": "Oracle"
}

extractor = ContentExtractor(Path("contract.pdf"), metadata)
extractor.consume_elements(elements)
content = extractor.get_processed_content()
```

### Indexing API

#### `store_data_in_vector_db(content, collection) -> None`

Store processed content in the vector database.

**Parameters:**
- `content` (list[dict]): Output from `ContentExtractor.get_processed_content()`
- `collection` (str): Target collection name

**Example:**
```python
from src.core.retriver.util.index_lib import store_data_in_vector_db

store_data_in_vector_db(content, "Page")
```

## Configuration APIs

### Configuration Management

#### Configuration Constants

Located in `src/core/config.py`:

```python
# Weaviate Schema Configuration
WEAVIATE_SCHEMA = {
    "class": "Page",
    "vectorizer": "text2vec-ollama",
    "properties": [...]
}

# LLM Configuration  
LLM_CONFIG = {
    "provider": "ollama",
    "model": "llama3.2", 
    "api_endpoint": "http://host.docker.internal:11434"
}

# System Messages for Different Tasks
LLM_SYSTEM_MESSAGES = {
    "entity_resolution": "...",
    "query_context_instructions": "..."
}

# File Paths
METADATA_CONFIG_PATH = os.environ.get("METADATA_CONFIG_PATH", "...")
DATA_FOLDER = os.environ.get("DATA_FOLDER", "...")
```

#### Environment Variables

- `METADATA_CONFIG_PATH`: Path to metadata.yml file
- `DATA_FOLDER`: Directory containing PDF documents

## Adapter APIs

### LLM Service Provider Interface

#### `LLMSPI` Abstract Base Class

**Location:** `src/core/spi/llm_spi.py`

##### `invoke_llm(prompt, system_message, **kwargs) -> str`

Abstract method for LLM invocation.

**Parameters:**
- `prompt` (str): User prompt text
- `system_message` (str): System instruction
- `**kwargs`: Provider-specific options

**Returns:**  
- `str`: LLM response text

#### `OllamaLLMSPAdapter` Implementation

**Location:** `src/sp_adapters/ollama_llm_sp_adapter.py`

**Constructor:**
```python
OllamaLLMSPAdapter(model: str = "llama3.2")
```

**Example:**
```python
from src.sp_adapters.ollama_llm_sp_adapter import OllamaLLMSPAdapter

adapter = OllamaLLMSPAdapter(model="llama3.2")
response = adapter.invoke_llm(
    prompt="What is a contract?", 
    system_message="You are a legal assistant."
)
```

### Vector Database Service Provider Interface

#### `VectorDBSPI` Abstract Base Class

**Location:** `src/core/spi/vector_db_spi.py`

##### Core Methods

```python
# Lifecycle
def connect() -> None
def close() -> None

# Schema Operations  
def create_schema(schema: dict) -> None
def drop_all_collections() -> None

# Data Operations
def insert_objects(collection: str, objects: Sequence[dict], batch_size: int = 100) -> None

# Search Operations
def search_bm25(collection: str, query: str, limit: int = 10, filters: FilterSpec = None) -> list[SearchResult]
def search_vector(collection: str, query: str, limit: int = 10, filters: FilterSpec = None) -> list[SearchResult] 
def search_hybrid(collection: str, query: str, limit: int = 10, filters: FilterSpec = None) -> list[SearchResult]
```

#### `SearchResult` Data Class

```python
@dataclass(frozen=True)
class SearchResult:
    properties: dict[str, Any]      # Document properties
    score: Optional[float] = None   # Similarity score (higher = better)
    distance: Optional[float] = None # Distance metric (lower = better)  
    id: Optional[str] = None        # Document ID
```

#### `WeaviateVectorDBAdapter` Implementation

**Location:** `src/sp_adapters/weaviate_adapter.py`

**Constructor:**
```python
WeaviateVectorDBAdapter(**connect_kwargs)
```

**Example:**
```python
from src.sp_adapters.weaviate_adapter import WeaviateVectorDBAdapter

adapter = WeaviateVectorDBAdapter()
adapter.connect()

# Search for documents
results = adapter.search_hybrid(
    collection="Page",
    query="payment terms",
    limit=5
)

adapter.close()
```

## Prompt Processing APIs

### Prompt Processor Functions

**Location:** `src/core/prompt_processor/prompt_processor.py`

#### `init(llm_adapter) -> None`

Initialize the prompt processor with an LLM adapter.

#### `extract_entities(prompt, system_message) -> str`

Extract entities from a query using the LLM.

**Parameters:**
- `prompt` (str): User query
- `system_message` (str): Entity extraction instructions

**Returns:**
- `str`: Extracted entities as text

#### `create_query_context(passages, query, instructions) -> str`

Build a context prompt from retrieved passages.

**Parameters:**
- `passages` (list[str]): Retrieved document content
- `query` (str): Original user query  
- `instructions` (str): System instructions for answering

**Returns:**
- `str`: Formatted prompt for answer generation

#### `generate_answer(prompt) -> str`

Generate an answer using the LLM.

**Parameters:**
- `prompt` (str): Complete prompt with context

**Returns:**
- `str`: Generated answer

**Example:**
```python
from src.core.prompt_processor import prompt_processor
from src.sp_adapters.ollama_llm_sp_adapter import OllamaLLMSPAdapter

# Initialize
adapter = OllamaLLMSPAdapter()
prompt_processor.init(adapter)

# Extract entities
entities = prompt_processor.extract_entities(
    prompt="What are Oracle's payment terms?",
    system_message="Extract entities from this query."
)

# Create context (after retrieving passages)
context = prompt_processor.create_query_context(
    passages=["Payment terms: Net 30 days", "Oracle requires..."],
    query="What are Oracle's payment terms?", 
    instructions="Answer based on the provided context."
)

# Generate answer
answer = prompt_processor.generate_answer(context)
```

## Error Handling

### Exception Types

#### `VectorDBError`
Raised for vector database connection and operation errors.

```python
try:
    adapter.connect()
except VectorDBError as e:
    print(f"Database connection failed: {e}")
```

#### `ValueError`
Raised for invalid input parameters.

```python
try:
    result = invoke_rag("", "hybrid", "Page", 5)
except ValueError as e:
    print(f"Invalid query: {e}")
```

#### `RuntimeError`
Raised when required adapters are not initialized.

```python
try:
    prompt_processor.extract_entities("query", "system")
except RuntimeError as e:
    print(f"LLM adapter not initialized: {e}")
```

### Best Practices

1. **Always initialize adapters** before use
2. **Use context managers** for database connections
3. **Validate inputs** before API calls
4. **Handle network timeouts** for external services
5. **Log errors** for debugging

```python
# Good pattern
from src.sp_adapters.weaviate_adapter import WeaviateVectorDBAdapter

with WeaviateVectorDBAdapter() as adapter:
    try:
        results = adapter.search_hybrid("Page", "query", limit=5)
    except VectorDBError as e:
        logger.error(f"Search failed: {e}")
        results = []
```

## Examples

### Complete RAG Workflow

```python
import yaml
from pathlib import Path
from src.core.rag import invoke_rag
from src.core.retriver.index_invoker import main as index_documents

# 1. Index documents (run once)
index_documents()

# 2. Query the system
answer = invoke_rag(
    query="What are the key terms in our Oracle agreement?",
    query_type="hybrid",
    collection="Page",
    limit=5
)

print("Answer:", answer)
```

### Custom Search Pipeline

```python
from src.core.retriver.util.search_lib import weaviate_search, add_metadata_filters
from src.sp_adapters.weaviate_adapter import WeaviateVectorDBAdapter
import src.core.retriver.util.search_lib as search_lib
import yaml

# Initialize database adapter
adapter = WeaviateVectorDBAdapter()
adapter.connect()
search_lib.init(adapter)

# Load metadata filters
config = yaml.safe_load(open("metadata.yml"))
filters = add_metadata_filters(config["metadata_filter_config"])

# Perform search
results = weaviate_search(
    query="termination conditions",
    type="hybrid",
    collection="Page", 
    limit=10,
    filters=filters
)

print(f"Found {len(results)} relevant passages")
for i, result in enumerate(results, 1):
    print(f"{i}. {result[:200]}...")

# Cleanup
adapter.close()
search_lib.clear_vector_db_adapter()
```

### Document Processing Pipeline

```python
from src.core.retriver.util.index_lib import (
    partition_pdf, ContentExtractor, store_data_in_vector_db
)
from src.sp_adapters.weaviate_adapter import WeaviateVectorDBAdapter
from pathlib import Path
from datetime import datetime

# Process a single document
pdf_path = Path("data/new_contract.pdf")
metadata = {
    "effective_date": datetime(2025, 1, 15),
    "provider": "Microsoft",
    "status": "active"
}

# Partition PDF
elements = partition_pdf(
    filename=pdf_path,
    infer_table_structure=True,
    unique_element_ids=True
)

# Extract content
extractor = ContentExtractor(pdf_path, metadata)
extractor.consume_elements(elements)
content = extractor.get_processed_content()

# Store in database
adapter = WeaviateVectorDBAdapter()
adapter.connect()
store_data_in_vector_db(content, "Page")
adapter.close()

print(f"Indexed {len(content)} pages from {pdf_path.name}")
```

This API documentation provides comprehensive coverage of all public interfaces in the Contract Inspector system. For implementation details, see the [Architecture Guide](ARCHITECTURE.md) and source code documentation.