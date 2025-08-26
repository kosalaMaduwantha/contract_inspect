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
# contract_inspect
AI legal contract screener - LLM | RAG
