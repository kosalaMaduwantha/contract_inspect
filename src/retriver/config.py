import os
WEAVIATE_SCHEMA = {
    "class": "Page",
    "vectorizer": "text2vec-ollama",  # Required: specify the vectorizer
    "properties": [
        {
            "name": "document",
            "dataType": ["text"],
            "description": "Original file name or URL",
            "moduleConfig": {
                "text2vec-ollama": {
                    "skip": True,  # Don't vectorize filenames
                    "vectorizePropertyName": False
                }
            }
        },
        {
            "name": "page_number",
            "dataType": ["int"],
            "description": "Page number in the original document"
        },
        {
            "name": "content",
            "dataType": ["text"],
            "description": "Main content of the file",
            "moduleConfig": {
                "text2vec-ollama": {
                    "skip": False,  # Explicitly vectorize content
                    "vectorizePropertyName": False
                }
            }
        },
        {
            "name": "effective_date",
            "dataType": ["date"],
            "description": "Date when the document was created"
        }
    ],
    "moduleConfig": {
        "generative-ollama": {
            "model": "llama3.2",
            "api_endpoint": "http://host.docker.internal:11434",
            "type": "text"
        },
        "text2vec-ollama": {
            "model": "nomic-embed-text",
            "api_endpoint": "http://host.docker.internal:11434",
            "type": "text"
        }
    }
}

METADATA_CONFIG_PATH = os.environ.get("METADATA_CONFIG_PATH", "/home/kosala/git-repos/contract_inspect/metadata.yml")
DATA_FOLDER = os.environ.get("DATA_FOLDER", "/home/kosala/git-repos/contract_inspect/data/")