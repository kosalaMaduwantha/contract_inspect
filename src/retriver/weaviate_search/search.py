import weaviate

def weaviate_search(query: str, type: str, collection: str, limit: int) -> any:

    client = weaviate.connect_to_local()
    if type == "bm25":
        pages = client.collections.get(collection)
        response = pages.query.bm25(
            query=query,
            limit=2,
        )
    elif type == "vector":
        pages = client.collections.get(collection)
        response = pages.query.near_text(
            query=query,
            limit=2,
        )
    elif type == "hybrid":
        pages = client.collections.get(collection)
        response = pages.query.hybrid(
            query=query,
            limit=2,
        )
    else:
        print("search type is not supported")
    client.close()
    return response