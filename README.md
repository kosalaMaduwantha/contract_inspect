
# Contract Inspector

An intelligent document analysis system that enables natural language querying of contract documents using Retrieval-Augmented Generation (RAG). Built with Weaviate vector database and Ollama LLM integration.

## 🚀 Features

- **Document Ingestion**: Automatic PDF contract processing and indexing
- **Intelligent Search**: BM25, vector, and hybrid search capabilities
- **Natural Language Queries**: Ask questions about contracts in plain English
- **Metadata Filtering**: Filter results by date ranges and document properties
- **RAG Pipeline**: Complete retrieval-augmented generation for accurate answers
- **Modular Architecture**: Clean separation with Service Provider Interfaces (SPI)

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Architecture](#architecture)
- [Usage](#usage)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## ⚡ Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Ollama** (if not already installed):
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ollama pull llama3.2
   ollama pull nomic-embed-text
   ```

3. **Start Weaviate**:
   ```bash
   docker compose -f compose-files/compose-weaviate.yml up -d
   ```

4. **Index your contracts**:
   ```bash
   cd src/core/retriver && python index_invoker.py
   ```

5. **Query your contracts**:
   ```bash
   cd src/core && python rag.py
   ```

## 🛠️ Installation

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- Ollama (for LLM functionality)

### Step 1: Clone the Repository

```bash
git clone https://github.com/kosalaMaduwantha/contract_inspect.git
cd contract_inspect
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Install and Configure Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull required models
ollama pull llama3.2      # For text generation
ollama pull nomic-embed-text  # For embeddings

# Start Ollama server (run in background)
ollama serve
```

### Step 4: Set up Weaviate Vector Database

```bash
# Start Weaviate using Docker Compose
docker compose -f compose-files/compose-weaviate.yml up -d

# Verify Weaviate is running
curl http://localhost:8080/v1/meta
```

### Step 5: Configure the System

1. Update paths in `src/core/config.py` if needed
2. Modify `metadata.yml` to match your contract documents
3. Place your PDF contracts in the `data/` directory (create if it doesn't exist)

## 🏗️ Architecture

The system follows a clean, modular architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │    │   PDF Docs      │    │   Configuration │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     RAG Pipeline                               │
├─────────┬───────────┬───────────┬───────────┬─────────────────┤
│ Entity  │ Document  │ Vector    │ Context   │ Answer          │
│Extract. │ Retrieval │ Search    │ Building  │ Generation      │
└─────────┴───────────┴───────────┴───────────┴─────────────────┘
          │           │           │           │
          ▼           ▼           ▼           ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Ollama LLM  │ │ Weaviate DB │ │ Search Lib  │ │ Prompt Proc │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

### Core Components

- **RAG Pipeline (`rag.py`)**: Orchestrates the entire query processing flow
- **Document Indexer (`index_invoker.py`)**: Processes and indexes PDF documents
- **Search Library (`search_lib.py`)**: Handles BM25, vector, and hybrid search
- **Prompt Processor**: Manages LLM interactions for entity extraction and answer generation
- **Service Provider Interfaces (SPI)**: Abstract interfaces for LLM and vector database
- **Adapters**: Concrete implementations for Ollama and Weaviate

## 📖 Usage

### Basic Query Example

```python
from src.core.rag import invoke_rag

# Ask a question about your contracts
result = invoke_rag(
    query="What are the termination conditions in the Oracle agreement?",
    query_type="hybrid",  # or "bm25", "vector"
    collection="Page",
    limit=5
)

print("Answer:", result)
```

### Indexing New Documents

```python
from src.core.retriver.index_invoker import main
from pathlib import Path

# Add new PDF to data directory
# Update metadata.yml with document info
# Run indexer
python src/core/retriver/index_invoker.py
```

### Advanced Search with Filters

```python
from src.core.retriver.util.search_lib import weaviate_search, add_metadata_filters
import yaml

# Load metadata configuration
metadata_config = yaml.safe_load(open("metadata.yml"))

# Search with date filtering
results = weaviate_search(
    query="payment terms",
    type="hybrid",
    collection="Page",
    limit=10,
    filters=add_metadata_filters(metadata_config["metadata_filter_config"])
)
```

## ⚙️ Configuration

### Main Configuration (`src/core/config.py`)

```python
# Weaviate Schema Configuration
WEAVIATE_SCHEMA = {
    "class": "Page",
    "vectorizer": "text2vec-ollama",
    "properties": [
        {"name": "document", "dataType": ["text"]},
        {"name": "page_number", "dataType": ["int"]},
        {"name": "content", "dataType": ["text"]},
        {"name": "effective_date", "dataType": ["date"]}
    ]
}

# LLM Configuration
LLM_CONFIG = {
    "provider": "ollama",
    "model": "llama3.2",
    "api_endpoint": "http://host.docker.internal:11434"
}
```

### Document Metadata (`metadata.yml`)

```yaml
service_agreements:
  - id: SA-001
    name: Oracle Cloud Agreement
    file_name: Oracle_Cloud_Agreement.pdf
    provider: Oracle
    effective_date: 2025-01-01
    expiration_date: 2026-01-01
    status: active

metadata_filter_config:
  effective_date:
    start: 2025-01-01
    end: 2026-01-01
```

## 📚 API Reference

### RAG Pipeline

#### `invoke_rag(query, query_type, collection, limit) -> str`

Main entry point for querying the contract database.

**Parameters:**
- `query` (str): Natural language question
- `query_type` (str): Search type - "bm25", "vector", or "hybrid"
- `collection` (str): Database collection name (typically "Page")
- `limit` (int): Maximum number of documents to retrieve

**Returns:** Generated answer as a string

### Search Functions

#### `weaviate_search(query, type, collection, limit, filters=None) -> list[str]`

Direct search interface for the vector database.

**Parameters:**
- `query` (str): Search query
- `type` (str): Search type - "bm25", "vector", or "hybrid"
- `collection` (str): Collection name
- `limit` (int): Result limit
- `filters` (optional): Metadata filters

**Returns:** List of matching document contents

### Document Processing

#### `partition_pdf(filename, **kwargs) -> list`

Processes PDF documents into structured elements.

**Parameters:**
- `filename` (Path): Path to PDF file
- `infer_table_structure` (bool): Extract table structure
- `include_page_breaks` (bool): Include page break markers
- `unique_element_ids` (bool): Generate unique IDs

**Returns:** List of document elements

## 💡 Examples

### Example 1: Contract Term Analysis

```python
from src.core.rag import invoke_rag

# Analyze payment terms
result = invoke_rag(
    query="What are the payment terms and schedule in our contracts?",
    query_type="hybrid",
    collection="Page",
    limit=3
)
print("Payment Terms:", result)
```

### Example 2: Compliance Checking

```python
# Check for specific clauses
result = invoke_rag(
    query="Are there any liability limitations in the Oracle agreement?",
    query_type="vector",
    collection="Page",
    limit=5
)
print("Liability Clauses:", result)
```

### Example 3: Contract Comparison

```python
# Compare multiple contracts
result = invoke_rag(
    query="Compare the termination clauses across all service agreements",
    query_type="hybrid",
    collection="Page",
    limit=10
)
print("Termination Comparison:", result)
```

## 🔧 Troubleshooting

### Common Issues

#### Weaviate Connection Error
```bash
# Check if Weaviate is running
curl http://localhost:8080/v1/meta

# Restart Weaviate
docker compose -f compose-files/compose-weaviate.yml restart
```

#### Ollama Model Not Found
```bash
# List available models
ollama list

# Pull missing models
ollama pull llama3.2
ollama pull nomic-embed-text
```

#### Import Path Issues
- Ensure you're running scripts from the correct directory
- Update PYTHONPATH if needed:
  ```bash
  export PYTHONPATH="${PYTHONPATH}:/path/to/contract_inspect"
  ```

#### Empty Search Results
- Verify documents are properly indexed
- Check metadata filters aren't too restrictive
- Try different search types (bm25, vector, hybrid)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](docs/CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests (when available)
5. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Add docstrings to public functions
- Include type hints where possible
- Keep functions focused and modular

## 📋 Project Structure

```
contract_inspect/
├── src/                          # Main source code
│   ├── core/                     # Core RAG system
│   │   ├── config.py            # Configuration settings
│   │   ├── rag.py               # Main RAG pipeline
│   │   ├── prompt_processor/    # LLM interaction handling
│   │   ├── retriver/            # Document retrieval logic
│   │   └── spi/                 # Service provider interfaces
│   └── sp_adapters/             # Service provider implementations
├── appendix/                     # Utility scripts
├── compose-files/               # Docker Compose configurations
├── data/                        # Document storage (create if needed)
├── metadata.yml                 # Document metadata configuration
├── requirements.txt             # Python dependencies
└── Makefile                     # Build automation
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Weaviate](https://weaviate.io/) for the vector database
- [Ollama](https://ollama.ai/) for local LLM capabilities
- [Unstructured](https://unstructured.io/) for document processing

---

**Python Version:** 3.12+

**Status:** Active Development

**Last Updated:** January 2025