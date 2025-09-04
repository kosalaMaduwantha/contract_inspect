from ollama import chat
from ollama import ChatResponse 
from src.retriver.config import OLLAMA_SYSTEM_MESSAGES

def extract_entities(prompt: str) -> list[str]:
    """Extract named entities from a given sentence using spaCy."""
    
    response: ChatResponse = chat(model='llama3.2', messages=[
        {
            'role': 'system',
            'content': OLLAMA_SYSTEM_MESSAGES['entity_resolution'],
        },
        {
            "role": "user", 
            "content": "What is the capital of sri lanka?"
        }
    ])

    return response['message']['content']
