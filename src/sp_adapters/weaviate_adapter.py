from typing import Any, Sequence
import weaviate
from weaviate.classes.query import MetadataQuery
from weaviate.classes.init import AdditionalConfig    
from weaviate import WeaviateClient                   
from src.core.spi.vector_db_spi import VectorDBSPI, SearchResult, VectorDBError, FilterSpec

class WeaviateVectorDBAdapter(VectorDBSPI):
    def __init__(self, **connect_kwargs: Any) -> None:
        self._client: weaviate.WeaviateClient | None = None
        self._connect_kwargs = connect_kwargs

    def connect(self) -> None:
        # Default to local unless overridden by kwargs
        self._client = weaviate.connect_to_local(**self._connect_kwargs)

    def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None

    def _require(self) -> weaviate.WeaviateClient:
        if not self._client:
            raise VectorDBError("Weaviate client not connected")
        return self._client

    def create_schema(self, schema: dict[str, Any]) -> None:
        client = self._require()
        client.collections.create_from_dict(schema)

    def drop_all_collections(self) -> None:
        client = self._require()
        client.collections.delete_all()

    def insert_objects(self, collection: str, objects: Sequence[dict[str, Any]], *, batch_size: int | None = 100) -> None:
        client = self._require()
        pages = client.collections.get(collection)
        bs = 100 if batch_size is None else int(batch_size)
        with pages.batch.fixed_size(batch_size=bs) as batch:
            for obj in objects:
                batch.add_object(obj)

    def search_bm25(self, collection: str, query: str, *, limit: int = 10, filters: FilterSpec | None = None) -> list[SearchResult]:
        client = self._require()
        pages = client.collections.get(collection)
        resp = pages.query.bm25(query=query, limit=limit, filters=filters)
        return [SearchResult(properties=o.properties, id=o.uuid) for o in resp.objects]

    def search_vector(self, collection: str, query: str, *, limit: int = 10, filters: FilterSpec | None = None, return_distance: bool = True) -> list[SearchResult]:
        client = self._require()
        pages = client.collections.get(collection)
        meta = MetadataQuery(distance=True) if return_distance else None
        resp = pages.query.near_text(query=query, limit=limit, filters=filters, return_metadata=meta)
        out: list[SearchResult] = []
        for o in resp.objects:
            dist = getattr(o.metadata, "distance", None) if hasattr(o, "metadata") else None
            out.append(SearchResult(properties=o.properties, distance=dist, id=o.uuid))
        return out

    def search_hybrid(self, collection: str, query: str, *, limit: int = 10, filters: FilterSpec | None = None) -> list[SearchResult]:
        client = self._require()
        pages = client.collections.get(collection)
        resp = pages.query.hybrid(query=query, limit=limit, filters=filters)
        return [SearchResult(properties=o.properties, id=o.uuid) for o in resp.objects]