import sys
from typing import Any, Optional

sys.path.append("/home/kosala/git-repos/contract_inspect/")

from weaviate.classes.query import Filter
from src.core.config import METADATA_CONFIG_PATH
from src.core.spi.vector_db_spi import (
    VectorDBSPI,
    SearchResult,
    VectorDBError,
    FilterSpec,
)
from src.sp_adapters.weaviate_adapter import WeaviateVectorDBAdapter
import yaml

"""Module to perform searches via a pluggable Vector DB adapter.

Mirrors the adapter wiring in index_lib.py and avoids direct client usage.
"""

# Module-level variable. Use _get_vector_db_adapter() to access safely.
vector_db_adapter: Optional[VectorDBSPI] = None


def init(adapter: Any) -> None:
    """Initialize the module-level vector DB adapter.

    Args:
        adapter: An object that implements the expected vector DB interface
                 (must provide the necessary methods for interaction).
    """
    global vector_db_adapter
    vector_db_adapter = adapter

def _get_vector_db_adapter() -> Any:
    """Return the initialized vector DB adapter or raise RuntimeError if missing."""
    if vector_db_adapter is None:
        raise RuntimeError("Vector DB adapter not initialized. Call init(adapter) first.")
    return vector_db_adapter

def clear_vector_db_adapter() -> None:
    """Clear the module-level adapter (useful for tests)."""
    global vector_db_adapter
    vector_db_adapter = None

def weaviate_search(
    query: str,
    type: str,
    collection: str,
    limit: int,
    filters: FilterSpec | None = None,
) -> list[str]:
    """Search via the configured Vector DB adapter and return content strings.

    The adapter must be initialized (and typically connected) via init(adapter).
    Returns the `content` property from each hit if present.
    """
    adapter = _get_vector_db_adapter()
    try:
        results: list[SearchResult]
        if type == "bm25":
            results = adapter.search_bm25(
                collection, 
                query, 
                limit=limit, 
                filters=filters
            )
        elif type == "vector":
            results = adapter.search_vector(
                collection, 
                query, 
                limit=limit, 
                filters=filters, 
                return_distance=True
            )
        elif type == "hybrid":
            results = adapter.search_hybrid(
                collection, 
                query, 
                limit=limit, 
                filters=filters
            )
        else:
            raise ValueError("search type is not supported")
    except (VectorDBError, Exception) as e:
        print("Error occurred while searching:", e)
        return []

    # Extract the `content` field if present.
    out: list[str] = []
    for r in results:
        props = r.properties or {}
        if "content" in props and isinstance(props["content"], str):
            out.append(props["content"])
    return out

def add_metadata_filters(filter_config: dict) -> FilterSpec:
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
    adapter = WeaviateVectorDBAdapter()
    init(adapter)
    adapter.connect()
    try:
        results = weaviate_search(
            query,
            type,
            collection,
            limit,
            filters=add_metadata_filters(metadata_config["metadata_filter_config"]),
        )
    finally:
        adapter.close()
    print("Search Results:", results)