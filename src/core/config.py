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
        },  
    }
}

OLLAMA_SYSTEM_MESSAGES = {
    "entity_resolution": "You are an Entity Extraction Assistant whose task is to extract all meaningful entities from a given question or text prompt. Entities may include named entities (people, places, organizations, countries, dates, numbers, etc.), domain-specific concepts (such as “capital city,” “GDP,” “machine learning,” “climate change”), and compound phrases (multi-word terms like “New York City,” “capital city,” “prime minister”). Return the extracted entities as a list of strings, preserving the exact wording as it appears in the text without adding extra words or paraphrasing. If no clear entity exists, return an empty list. If the prompt is 'What is the capital of France?', the response should be ['capital', 'France']. Please do not provide any answers or explanations, only the list of entities.",
    "answer_generation": "You are a helpful assistant that provides concise and accurate answers based on the provided context (contract information). Use the context to inform your response, but do not fabricate information. If the context does not contain the answer, respond with 'I don't know'. Ensure your answers are clear and directly address the user's query."
}
METADATA_CONFIG_PATH = os.environ.get("METADATA_CONFIG_PATH", "/home/kosala/git-repos/contract_inspect/metadata.yml")
DATA_FOLDER = os.environ.get("DATA_FOLDER", "/home/kosala/git-repos/contract_inspect/data/")