
WEAVIATE_SCHEMA = {
    "class": "Page",
    "properties": [
        {
            "name": "document",
            "dataType": ["text"],
            "description": "Original file name or URL",
        },
        {
            "name": "page_number",
            "dataType": ["int"],
            "description": "Page number in the original document"
        },
        {
            "name": "content",
            "dataType": ["text"],
            "description": "Main content of the file"
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