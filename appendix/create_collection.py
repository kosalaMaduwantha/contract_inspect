import weaviate
from weaviate.classes.config import Configure

client = weaviate.Client()

client.collections.delete("Question")  # Delete the collection if it exists
questions = client.collections.create(
    name="Question",
    vector_config=Configure.Vectors.text2vec_ollama(  # Configure the Ollama embedding integration
        api_endpoint="http://host.docker.internal:11434",  # If using Docker you might need: http://host.docker.internal:11434
        model="nomic-embed-text",  # The model to use
    ),
    generative_config=Configure.Generative.ollama(  # Configure the Ollama generative integration
        api_endpoint="http://host.docker.internal:11434",  # If using Docker you might need: http://host.docker.internal:11434
        model="llama3.2",  # The model to use
    ),
)

client.close()  # Free up resources