from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterable, Optional, Sequence


class VectorDBError(Exception):
	"""Generic vector database error."""


@dataclass(frozen=True)
class SearchResult:
	"""A provider-agnostic search result item.

	Attributes:
		properties: The stored object/document properties returned by the DB.
		score: Optional similarity score (higher-is-better). Some providers
			   return distance instead; if so, leave this None and populate
			   `distance`.
		distance: Optional distance metric (lower-is-better). If the backend
				  returns a score instead, leave this as None.
		id: Optional provider-specific object identifier.
	"""

	properties: dict[str, Any]
	score: Optional[float] = None
	distance: Optional[float] = None
	id: Optional[str] = None


FilterSpec = Any  # Provider-specific filter structure (e.g., Weaviate Filter)


class VectorDBSPI(ABC):
	"""Service Provider Interface (SPI) for vector-capable databases.

	This defines the minimal contract used by retrievers and indexers. It is
	intentionally small and provider-agnostic, while matching the operations
	used in the current Weaviate-based implementation (schema creation,
	batching inserts, and bm25/vector/hybrid search with optional filters).
	"""

	# ---- Lifecycle ----
	@abstractmethod
	def connect(self) -> None:
		"""Establish a connection/session to the backing store."""

	@abstractmethod
	def close(self) -> None:
		"""Close the underlying connection/session and release resources."""

	# Optional ergonomic context-manager helpers
	def __enter__(self) -> "VectorDBSPI":
		self.connect()
		return self

	def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
		self.close()

	# ---- Schema / Collections ----
	@abstractmethod
	def create_schema(self, schema: dict[str, Any]) -> None:
		"""Create or update collections/classes per the provided schema.

		Implementations may choose to drop existing conflicting collections.
		The schema structure is provider-specific and passed through as-is.
		"""

	@abstractmethod
	def drop_all_collections(self) -> None:
		"""Drop all collections/classes in the database (destructive)."""

	# ---- Ingest / Insert ----
	@abstractmethod
	def insert_objects(
		self,
		collection: str,
		objects: Sequence[dict[str, Any]],
		*,
		batch_size: int | None = 100,
	) -> None:
		"""Insert a list of objects/documents into a collection.

		Args:
			collection: Target collection/class name.
			objects: Iterable of property dictionaries to insert.
			batch_size: Optional batching hint for backends that support it.
		"""

	# ---- Search ----
	@abstractmethod
	def search_bm25(
		self,
		collection: str,
		query: str,
		*,
		limit: int = 10,
		filters: FilterSpec | None = None,
	) -> list[SearchResult]:
		"""BM25 keyword search.

		Returns provider-agnostic results preserving stored properties.
		"""

	@abstractmethod
	def search_vector(
		self,
		collection: str,
		query: str,
		*,
		limit: int = 10,
		filters: FilterSpec | None = None,
		return_distance: bool = True,
	) -> list[SearchResult]:
		"""Vector similarity search for a natural language query.

		Implementations may choose the best mapping (e.g., near_text).
		"""

	@abstractmethod
	def search_hybrid(
		self,
		collection: str,
		query: str,
		*,
		limit: int = 10,
		filters: FilterSpec | None = None,
	) -> list[SearchResult]:
		"""Hybrid (keyword + vector) search for the query string."""


__all__ = [
	"VectorDBSPI",
	"VectorDBError",
	"SearchResult",
	"FilterSpec",
]

