# Architecture Guide

This document provides a comprehensive overview of the Contract Inspector system architecture, design decisions, and implementation details.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Component Details](#component-details)
- [Data Flow](#data-flow)
- [Design Patterns](#design-patterns)
- [Technology Stack](#technology-stack)
- [Performance Considerations](#performance-considerations)
- [Security](#security)
- [Extensibility](#extensibility)

## Overview

Contract Inspector is a Retrieval-Augmented Generation (RAG) system designed to enable natural language querying of contract documents. The system combines document processing, vector search, and large language models to provide accurate, contextual answers to questions about contract content.

### Core Principles

- **Modular Design**: Clear separation of concerns with well-defined interfaces
- **Pluggable Components**: Easy to swap implementations (different LLMs, vector DBs)
- **Scalability**: Designed to handle large document sets efficiently
- **Accuracy**: Combines multiple search strategies for better retrieval
- **Maintainability**: Clean code structure with comprehensive documentation

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          User Interface                        │
└─────────────────────┬───────────────────────────────────────────┘
                      │ Natural Language Query
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                        RAG Pipeline                            │
├─────────────┬─────────────┬─────────────┬─────────────────────┤
│   Entity    │  Document   │   Vector    │      Answer         │
│ Extraction  │  Retrieval  │   Search    │    Generation       │
└─────┬───────┴─────┬───────┴─────┬───────┴─────────┬───────────┘
      │             │             │                 │
      ▼             ▼             ▼                 ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│             │ │             │ │             │ │             │
│ Ollama LLM  │ │ Weaviate DB │ │ Search Lib  │ │ Prompt Proc │
│             │ │             │ │             │ │             │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
      │             │             │                 │
      └─────────────┼─────────────┼─────────────────┘
                    │             │
                    ▼             ▼
              ┌─────────────────────────┐
              │   Service Provider      │
              │     Interfaces (SPI)    │
              └─────────────────────────┘
```

### Component Layer Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Application Layer                          │
├─────────────────────────────────────────────────────────────────┤
│ rag.py │ index_invoker.py │ prompt_processor.py                 │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│                      Core Layer                                │
├─────────────────────────────────────────────────────────────────┤
│ search_lib.py │ index_lib.py │ config.py                       │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│                      SPI Layer                                 │
├─────────────────────────────────────────────────────────────────┤
│ llm_spi.py │ vector_db_spi.py                                   │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│                    Adapter Layer                               │
├─────────────────────────────────────────────────────────────────┤
│ ollama_llm_sp_adapter.py │ weaviate_adapter.py                 │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                          │
├─────────────────────────────────────────────────────────────────┤
│ Ollama LLM │ Weaviate Vector DB │ Docker │ Unstructured       │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. RAG Pipeline (`src/core/rag.py`)

**Purpose**: Orchestrates the complete query processing workflow

**Key Functions**:
- `invoke_rag()`: Main entry point for query processing

**Workflow**:
1. Initialize LLM and vector DB adapters
2. Extract entities from user query using LLM
3. Perform vector/hybrid search using extracted entities
4. Construct context from retrieved documents
5. Generate final answer using LLM

```python
def invoke_rag(query: str, query_type: str, collection: str, limit: int) -> str:
    # Entity extraction
    extracted_entities = prompt_processor.extract_entities(query, system_message)
    
    # Document retrieval
    results = search_lib.weaviate_search(query, query_type, collection, limit, filters)
    
    # Context construction
    augmented_prompt = prompt_processor.create_query_context(results, query, instructions)
    
    # Answer generation
    answer = prompt_processor.generate_answer(augmented_prompt)
    return answer
```

### 2. Document Indexing (`src/core/retriver/index_invoker.py`)

**Purpose**: Processes and indexes PDF documents into the vector database

**Process**:
1. Read metadata configuration
2. For each document:
   - Partition PDF using Unstructured library
   - Extract content with metadata
   - Store in Weaviate with embeddings

**Key Features**:
- Page-by-page processing
- Metadata preservation
- Automatic schema creation

### 3. Search Library (`src/core/retriver/util/search_lib.py`)

**Purpose**: Provides unified search interface supporting multiple search strategies

**Search Types**:
- **BM25**: Keyword-based search using TF-IDF scoring
- **Vector**: Semantic search using embeddings
- **Hybrid**: Combines BM25 and vector search for optimal relevance

**Features**:
- Metadata filtering
- Configurable result limits
- Error handling and fallbacks

### 4. Prompt Processor (`src/core/prompt_processor/prompt_processor.py`)

**Purpose**: Manages all LLM interactions with specialized prompts

**Functions**:
- `extract_entities()`: Extracts relevant entities from user queries
- `create_query_context()`: Builds context from retrieved documents
- `generate_answer()`: Generates final answers using context

**Prompt Engineering**:
- System messages for different tasks
- Context-aware prompt construction
- Error handling for LLM failures

### 5. Service Provider Interfaces (SPI)

#### LLM SPI (`src/core/spi/llm_spi.py`)

**Purpose**: Abstract interface for language model providers

```python
class LLMSPI(ABC):
    @abstractmethod
    def invoke_llm(self, prompt: str, system_message: str, **kwargs) -> str:
        pass
```

**Benefits**:
- Provider independence
- Easy testing with `EchoLLM`
- Consistent interface across components

#### Vector DB SPI (`src/core/spi/vector_db_spi.py`)

**Purpose**: Abstract interface for vector database providers

```python
class VectorDBSPI(ABC):
    @abstractmethod
    def search_bm25(self, collection: str, query: str, **kwargs) -> list[SearchResult]:
        pass
    
    @abstractmethod
    def search_vector(self, collection: str, query: str, **kwargs) -> list[SearchResult]:
        pass
    
    @abstractmethod
    def search_hybrid(self, collection: str, query: str, **kwargs) -> list[SearchResult]:
        pass
```

### 6. Adapter Layer

#### Ollama LLM Adapter (`src/sp_adapters/ollama_llm_sp_adapter.py`)

**Purpose**: Implements LLM SPI for Ollama provider

**Features**:
- Configurable model selection
- System message support
- Response parsing and error handling

#### Weaviate Adapter (`src/sp_adapters/weaviate_adapter.py`)

**Purpose**: Implements Vector DB SPI for Weaviate

**Features**:
- Connection management
- Schema operations
- Multi-modal search (BM25, vector, hybrid)
- Batch operations for indexing

## Data Flow

### Document Indexing Flow

```
PDF Document
     │
     ▼
┌─────────────────┐
│ Unstructured    │ ── Partition into elements
│ PDF Processor   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Content         │ ── Extract text + metadata
│ Extractor       │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Weaviate        │ ── Store with embeddings
│ Vector DB       │
└─────────────────┘
```

### Query Processing Flow

```
User Query
     │
     ▼
┌─────────────────┐
│ Entity          │ ── Extract key entities
│ Extraction      │    using LLM
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Vector Search   │ ── Retrieve relevant docs
│ (BM25/Vector/   │    with metadata filters
│  Hybrid)        │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Context         │ ── Build prompt with
│ Construction    │    retrieved content
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Answer          │ ── Generate final answer
│ Generation      │    using LLM
└─────────────────┘
```

## Design Patterns

### 1. Service Provider Interface Pattern

**Problem**: Need to support multiple LLM and vector DB providers

**Solution**: Abstract interfaces with concrete adapters

**Benefits**:
- Loose coupling
- Easy testing
- Provider flexibility

### 2. Strategy Pattern

**Problem**: Multiple search strategies (BM25, vector, hybrid)

**Solution**: Unified search interface with configurable strategy

**Implementation**:
```python
def weaviate_search(query, type, collection, limit, filters=None):
    if type == "bm25":
        return adapter.search_bm25(collection, query, limit=limit, filters=filters)
    elif type == "vector":
        return adapter.search_vector(collection, query, limit=limit, filters=filters)
    elif type == "hybrid":
        return adapter.search_hybrid(collection, query, limit=limit, filters=filters)
```

### 3. Factory Pattern

**Problem**: Creating different types of adapters

**Solution**: Configuration-driven adapter creation

**Implementation**:
```python
def create_llm_adapter(config):
    if config["provider"] == "ollama":
        return OllamaLLMSPAdapter(model=config["model"])
    elif config["provider"] == "openai":
        return OpenAILLMSPAdapter(api_key=config["api_key"])
```

### 4. Template Method Pattern

**Problem**: Consistent RAG pipeline with customizable steps

**Solution**: Fixed pipeline structure with pluggable components

## Technology Stack

### Core Technologies

- **Python 3.12+**: Main programming language
- **Weaviate**: Vector database for document storage and search
- **Ollama**: Local LLM inference server
- **Unstructured**: PDF processing and document parsing
- **Docker**: Containerization for easy deployment

### Python Libraries

- **weaviate-client**: Weaviate Python SDK
- **ollama**: Ollama Python client
- **yaml**: Configuration file parsing
- **pathlib**: Modern path handling
- **logging**: Comprehensive logging
- **typing**: Type hints for better code quality

### Models

- **llama3.2**: Primary language model for reasoning
- **nomic-embed-text**: Embedding model for vector search

## Performance Considerations

### Scalability Factors

1. **Document Volume**: System scales with number of documents
2. **Query Complexity**: Complex queries require more computation
3. **Search Strategy**: Hybrid search is most comprehensive but slowest
4. **Model Size**: Larger models provide better quality but slower inference

### Optimization Strategies

#### 1. Indexing Optimizations

```python
# Batch processing for large document sets
batch_size = 100  # Adjust based on memory
for i in range(0, len(documents), batch_size):
    batch = documents[i:i+batch_size]
    adapter.insert_objects(collection, batch, batch_size=batch_size)
```

#### 2. Search Optimizations

```python
# Use appropriate search strategy
- BM25: Fast, good for keyword matching
- Vector: Slower, good for semantic similarity
- Hybrid: Balanced, best overall quality
```

#### 3. Caching Strategies

- Cache frequently accessed documents
- Cache embedding computations
- Cache search results for repeated queries

### Memory Management

- **Weaviate**: Configure appropriate memory limits
- **Ollama**: Consider model quantization for memory efficiency
- **Python**: Use generators for large data processing

## Security

### Data Security

1. **Document Storage**: Documents stored locally in Weaviate
2. **Network Security**: Local-only deployment by default
3. **Access Control**: No built-in authentication (add as needed)

### Privacy Considerations

1. **Local Processing**: All data processing happens locally
2. **No External APIs**: No data sent to external services (except if configured)
3. **Audit Trail**: All operations are logged

### Security Best Practices

```bash
# Use Docker networks for isolation
docker network create contract_inspect_network

# Restrict Weaviate to localhost
# In compose-weaviate.yml:
ports:
  - "127.0.0.1:8080:8080"  # Localhost only

# Use environment variables for sensitive config
export WEAVIATE_API_KEY="your-secure-key"
```

## Extensibility

### Adding New LLM Providers

1. Implement `LLMSPI` interface:
```python
class CustomLLMAdapter(LLMSPI):
    def invoke_llm(self, prompt: str, system_message: str, **kwargs) -> str:
        # Your implementation
        pass
```

2. Update configuration:
```python
LLM_CONFIG = {
    "provider": "custom",
    "api_endpoint": "https://api.custom-llm.com"
}
```

### Adding New Vector DB Providers

1. Implement `VectorDBSPI` interface:
```python
class CustomVectorDBAdapter(VectorDBSPI):
    def search_bm25(self, collection: str, query: str, **kwargs) -> list[SearchResult]:
        # Your implementation
        pass
```

### Adding New Document Types

1. Extend `ContentExtractor`:
```python
class WordDocExtractor(ContentExtractor):
    def process_document(self, doc_path):
        # Process Word documents
        pass
```

2. Update indexing logic to handle new types

### Adding New Search Strategies

1. Extend search library:
```python
def search_semantic_rerank(query, collection, limit, filters=None):
    # Implementation for semantic reranking
    pass
```

2. Update search type selection logic

## Future Enhancements

### Planned Features

1. **ReRanking Module**: Improve search result quality
2. **Multi-modal Support**: Handle images and tables in contracts
3. **Real-time Updates**: Live document indexing
4. **Advanced Analytics**: Query pattern analysis
5. **Web Interface**: User-friendly web UI
6. **API Server**: REST API for integration

### Architecture Evolution

1. **Microservices**: Split into independent services
2. **Message Queues**: Async processing for large document sets
3. **Caching Layer**: Redis for performance optimization
4. **Load Balancing**: Multiple LLM/DB instances
5. **Monitoring**: Comprehensive observability stack

## Conclusion

The Contract Inspector architecture provides a solid foundation for document analysis with clear separation of concerns, extensible design, and focus on performance. The modular approach allows for easy customization and scaling as requirements evolve.