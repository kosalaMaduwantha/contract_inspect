import weaviate
from weaviate.classes.query import MetadataQuery

def weaviate_search(query: str, type: str, collection: str, limit: int) -> any:
    response = None
    try:
        client = weaviate.connect_to_local()
        if type == "bm25":
            pages = client.collections.get(collection)
            response = pages.query.bm25(
                query=query,
                limit=limit,
            )
        elif type == "vector": # TODO: fix bug in vector search
            pages = client.collections.get(collection)
            response = pages.query.near_text(
                query=query,
                limit=limit,
                return_metadata=MetadataQuery(distance=True)
            )
        elif type == "hybrid":
            pages = client.collections.get(collection)
            response = pages.query.hybrid(
                query=query,
                limit=limit,
            )
        else:
            print("search type is not supported")
        client.close()
    except Exception as e:
        print("Error occurred while searching:", e)
        client.close()
    return response

def add_metadata_filters():
    # create set of metadata filters using a configuration
    pass

if __name__ == "__main__":
    query = "oracle"
    type = "hybrid"  # or "vector" or "hybrid"
    collection = "Page"
    limit = 5

    results = weaviate_search(query, type, collection, limit)
    print("Search Results:", results)