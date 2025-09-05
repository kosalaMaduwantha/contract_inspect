import sys

sys.path.append("/home/kosala/git-repos/contract_inspect/")
sys.path.append("/home/kosala/git-repos/contract_inspect/src")
import yaml
from core.retriver.util import search_lib
from sp_adapters.weaviate_adapter import WeaviateVectorDBAdapter
from core.config import METADATA_CONFIG_PATH
from core.retriver.util.search_lib import weaviate_search, add_metadata_filters
from src.core.prompt_processor import prompt_processor
from src.sp_adapters.ollama_llm_sp_adapter import OllamaLLMSPAdapter
from core.config import LLM_SYSTEM_MESSAGES

def invoke_rag(query: str, query_type: str, collection: str, limit: int) -> any:
    metadata_config = yaml.safe_load(open(METADATA_CONFIG_PATH))

    # invoke llm to extract entities from the query
    prompt_processor.init(OllamaLLMSPAdapter())
    extracted_entities = prompt_processor.extract_entities(
        prompt=query,
        system_message=LLM_SYSTEM_MESSAGES['entity_resolution']
    )
    extracted_entities = "".join(extracted_entities)
    
    # call weaviate to search for relevant documents
    # initialize vector db client
    weaviate_adapter = WeaviateVectorDBAdapter()
    weaviate_adapter.connect()
    search_lib.init(adapter=weaviate_adapter)

    # perform the search
    results = search_lib.weaviate_search(
        query=extracted_entities,
        type=query_type,
        collection=collection,
        limit=limit,
        filters=search_lib.add_metadata_filters(
            metadata_config["metadata_filter_config"]
        )
    )
    weaviate_adapter.close()
    search_lib.clear_vector_db_adapter()
    
    # construct the prompt for final answer generation
    augmented_prompt = prompt_processor.create_query_context(
        passages=results,
        query=query,
        instructions=LLM_SYSTEM_MESSAGES['query_context_instructions']
    )
    
    # answer generation using llm
    results = prompt_processor.generate_answer(
        prompt=augmented_prompt
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