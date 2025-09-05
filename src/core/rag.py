import sys
sys.path.append("/home/kosala/git-repos/contract_inspect/")
sys.path.append("/home/kosala/git-repos/contract_inspect/src")
import yaml
from core.config import METADATA_CONFIG_PATH
from core.retriver.util.search_lib import weaviate_search, add_metadata_filters
from src.core.prompt_processor import prompt_processor
from src.sp_adapters.ollama_llm_sp_adapter import OllamaLLMSPAdapter
from core.config import OLLAMA_SYSTEM_MESSAGES

def invoke_rag(query: str, query_type: str, collection: str, limit: int) -> any:
    metadata_config = yaml.safe_load(open(METADATA_CONFIG_PATH))

    # invoke llm to extract entities from the query
    prompt_processor.init(OllamaLLMSPAdapter())
    extracted_entities = prompt_processor.extract_entities(
        prompt=query,
        system_message=OLLAMA_SYSTEM_MESSAGES['entity_resolution']
    )
    extracted_entities = "".join(extracted_entities)
    
    # call weaviate to search for relevant documents
    results = weaviate_search(
        query=extracted_entities, 
        type=query_type, 
        collection=collection, 
        limit=limit, 
        filters=add_metadata_filters(
            metadata_config["metadata_filter_config"]
        )
    )
    
    # construct the prompt for final answer generation
    augmented_prompt = prompt_processor.create_query_context(
        passages=results,
        query=query,
    )
    
    # answer generation using llm
    results = prompt_processor.generate_answer(
        prompt=augmented_prompt,
        system_message=OLLAMA_SYSTEM_MESSAGES['answer_generation']
    )
    return results
    

if __name__ == "__main__":
    query = "what is oracle open source agreement?"
    type = "hybrid"  # or "vector" or "hybrid"
    collection = "Page"
    limit = 2
    metadata_config = yaml.safe_load(open(METADATA_CONFIG_PATH))
    
    results = invoke_rag(query, type, collection, limit)
    print("results:", results)