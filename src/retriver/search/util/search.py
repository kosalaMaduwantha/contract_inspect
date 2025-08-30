import sys
sys.path.append("/home/kosala/git-repos/contract_inspect/")
import weaviate
from weaviate.classes.query import MetadataQuery, Filter
from src.retriver.config import METADATA_CONFIG_PATH
import yaml

def weaviate_search(query: str, type: str, collection: str, limit: int, filters: tuple=None) -> any:
    response = None
    try:
        client = weaviate.connect_to_local()
        if type == "bm25":
            pages = client.collections.get(collection)
            response = pages.query.bm25(
                query=query,
                limit=limit,
                filters=filters
            )
        elif type == "vector": # TODO: fix bug in vector search
            pages = client.collections.get(collection)
            response = pages.query.near_text(
                query=query,
                limit=limit,
                return_metadata=MetadataQuery(distance=True),
                filters=filters
            )
        elif type == "hybrid":
            pages = client.collections.get(collection)
            response = pages.query.hybrid(
                query=query,
                limit=limit,
                filters=filters,
            )
        else:
            print("search type is not supported")
        client.close()
    except Exception as e:
        print("Error occurred while searching:", e)
        client.close()
    return response

def add_metadata_filters(filter_config: dict) -> tuple:
    # create set of metadata filters using a configuration
    filters = (
        Filter.by_property(
            "effective_date").greater_or_equal(
                filter_config["effective_date"]["start"])
    )
    return filters

if __name__ == "__main__":
    query = "oracle"
    type = "hybrid"  # or "vector" or "hybrid"
    collection = "Page"
    limit = 5

    metadata_config = yaml.safe_load(open(METADATA_CONFIG_PATH))
    results = weaviate_search(
        query, type, collection, limit, 
        filters=add_metadata_filters(
            metadata_config["metadata_filter_config"]
        )
    )
    print("Search Results:", results)