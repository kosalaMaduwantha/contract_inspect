import sys
sys.path.append("/home/kosala/git-repos/contract_inspect/")
import yaml
from src.retriver.config import METADATA_CONFIG_PATH
from src.retriver.search.util.search_lib import weaviate_search, add_metadata_filters
from src.query_parser.utils.parser_lib import extract_entities


if __name__ == "__main__":
    query = "what is oracle"
    type = "hybrid"  # or "vector" or "hybrid"
    collection = "Page"
    limit = 5
    metadata_config = yaml.safe_load(open(METADATA_CONFIG_PATH))
    
    extracted_entities = extract_entities(query)
    extracted_entities = " ".join(extracted_entities)
    results = weaviate_search(
        query, type, collection, limit, 
        filters=add_metadata_filters(
            metadata_config["metadata_filter_config"]
        )
    )
    print("Search Results:", results)