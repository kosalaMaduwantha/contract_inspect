import weaviate

def weaviate_search(query: str, type: str, collection: str, limit: int) -> any:

    client = weaviate.connect_to_local()
    if type == "bm25":
        pages = client.collections.get(collection)
        response = pages.query.bm25(
            query=query,
            limit=limit,
        )
    elif type == "vector":
        pages = client.collections.get(collection)
        response = pages.query.near_text(
            query=query,
            limit=limit,
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
    return response