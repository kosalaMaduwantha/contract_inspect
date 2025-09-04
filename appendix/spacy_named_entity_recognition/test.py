from ollama import chat
from ollama import ChatResponse 

response: ChatResponse = chat(model='llama3.2', messages=[
  {
    'role': 'system',
    'content': "You are an Entity Extraction Assistant whose task is to extract all meaningful entities from a given question or text prompt. Entities may include named entities (people, places, organizations, countries, dates, numbers, etc.), domain-specific concepts (such as “capital city,” “GDP,” “machine learning,” “climate change”), and compound phrases (multi-word terms like “New York City,” “capital city,” “prime minister”). Return the extracted entities as a list of strings, preserving the exact wording as it appears in the text without adding extra words or paraphrasing. If no clear entity exists, return an empty list. If the prompt is 'What is the capital of France?', the response should be ['capital', 'France']. Please do not provide any answers or explanations, only the list of entities.",
  },
  {
      "role": "user", 
      "content": "What is the capital of sri lanka?"
  }
])
print(response['message']['content'])
# or access fields directly from the response object